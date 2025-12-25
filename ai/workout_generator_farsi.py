"""
Farsi Workout Plan Generator using AvalAI API and SQL-Based Exercise Database
Generates personalized weekly workout plans in Farsi based on user profile
"""
import os
import json
import requests
import psycopg2
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
AVALAI_BASE_URL = "https://api.avalai.ir"

# Get API key from settings when imported as module, or from env for standalone testing
try:
    from app.core.config import settings
    AVALAI_API_KEY = settings.AVALAI_API_KEY
except ImportError:
    # Fallback for standalone testing
    from dotenv import load_dotenv
    load_dotenv()
    AVALAI_API_KEY = os.getenv("x-goog-api-key")

if not AVALAI_API_KEY:
    raise ValueError("x-goog-api-key not found in .env file or settings")

# Gemini model configuration
GEMINI_MODEL = "gemini-2.5-pro"


# ─────────────────────────────────────────────
# SQL-BASED EXERCISE SEARCH ENGINE
# ─────────────────────────────────────────────
class FarsiExerciseSearchEngine:
    """
    SQL-based search engine for finding relevant exercises using filters.
    Returns exercises with Farsi names and instructions.
    """
    
    def search_exercises(self, 
                        db: Session,
                        difficulty: Optional[str] = None,
                        muscle_groups: Optional[List[str]] = None,
                        equipment_ids: Optional[List[int]] = None,
                        training_phase: Optional[str] = None,
                        style: Optional[str] = None,
                        limit: int = 50) -> List[Dict]:
        """
        Search for exercises using SQL filters.
        
        Args:
            db: SQLAlchemy database session
            difficulty: Difficulty level (Beginner, Novice, Intermediate, Advanced)
            muscle_groups: Target muscle groups in English
            equipment_ids: Available equipment IDs
            training_phase: Workout phase (Warm-up, Main, Cool-down)
            style: Exercise style (Recovery, Stretches, Cardio)
            limit: Maximum number of results
            
        Returns:
            List[Dict]: List of exercises with full details in Farsi
        """
        
        query_parts = ["""
            SELECT
                e.exercise_id,
                e.name_en,
                e.name_fa,
                e.instructions_fa,
                e.male_urls,
                e.male_image_urls,
                d.name_fa as difficulty_fa,
                d.difficulty_id,
                ARRAY_AGG(DISTINCT eq.name_fa) FILTER (WHERE eq.name_fa IS NOT NULL) as equipment_names,
                ARRAY_AGG(DISTINCT eq.equipment_id) FILTER (WHERE eq.equipment_id IS NOT NULL) as equipment_ids,
                ARRAY_AGG(DISTINCT m.name_fa) FILTER (WHERE m.name_fa IS NOT NULL) as muscle_names,
                ARRAY_AGG(DISTINCT m.muscle_id) FILTER (WHERE m.muscle_id IS NOT NULL) as muscle_ids
            FROM exercise e
            LEFT JOIN difficulty d ON e.difficulty_id = d.difficulty_id
            LEFT JOIN exercise_equipment ee ON e.exercise_id = ee.exercise_id
            LEFT JOIN equipment eq ON ee.equipment_id = eq.equipment_id
            LEFT JOIN exercise_muscle em ON e.exercise_id = em.exercise_id
            LEFT JOIN muscle m ON em.muscle_id = m.muscle_id
            LEFT JOIN style s ON e.style_id = s.style_id
        """]
        
        conditions = []
        params = {}
        
        # Filter by difficulty
        if difficulty:
            conditions.append("d.name_en = :difficulty")
            params['difficulty'] = difficulty
        
        # Filter by equipment
        if equipment_ids:
            conditions.append("EXISTS (SELECT 1 FROM exercise_equipment ee_filter WHERE ee_filter.exercise_id = e.exercise_id AND ee_filter.equipment_id = ANY(:equipment_ids))")
            params['equipment_ids'] = equipment_ids
        
        # Filter by muscle groups
        if muscle_groups:
            conditions.append("EXISTS (SELECT 1 FROM exercise_muscle em_filter JOIN muscle m_filter ON em_filter.muscle_id = m_filter.muscle_id WHERE em_filter.exercise_id = e.exercise_id AND m_filter.name_en = ANY(:muscle_groups))")
            params['muscle_groups'] = muscle_groups
        
        # Filter by style
        if style:
            conditions.append("s.name_en = :style")
            params['style'] = style
        
        # Add WHERE clause
        if conditions:
            query_parts.append("WHERE " + " AND ".join(conditions))
        
        # Add GROUP BY and ORDER BY RANDOM() and LIMIT
        query_parts.append("""
            GROUP BY e.exercise_id, e.name_en, e.name_fa, e.instructions_fa, 
                     e.male_urls, e.male_image_urls, d.name_fa, d.difficulty_id
            ORDER BY RANDOM()
            LIMIT :limit
        """)
        params['limit'] = limit
        
        # Execute query
        full_query = " ".join(query_parts)
        result = db.execute(text(full_query), params)
        
        exercises = []
        for row in result:
            exercises.append({
                'exercise_id': row[0],
                'name_en': row[1],
                'name_fa': row[2],
                'instructions_fa': row[3] or [],
                'male_urls': row[4] or [],
                'male_image_urls': row[5] or [],
                'difficulty_fa': row[6],
                'difficulty_id': row[7],
                'equipment_names': row[8] or [],
                'equipment_ids': row[9] or [],
                'muscle_names': row[10] or [],
                'muscle_ids': row[11] or []
            })
        
        return exercises
    
    def search_warmup_exercises(self, db: Session, muscle_focus: Optional[str] = None, 
                                equipment_ids: Optional[List[int]] = None, limit: int = 15) -> List[Dict]:
        """Search for warmup exercises"""
        # For warmup, we look for stretches and recovery exercises
        return self.search_exercises(
            db=db,
            style='Stretches',
            muscle_groups=[muscle_focus] if muscle_focus else None,
            equipment_ids=equipment_ids,
            limit=limit
        )
    
    def search_cooldown_exercises(self, db: Session, muscle_focus: Optional[str] = None,
                                  limit: int = 15) -> List[Dict]:
        """Search for cooldown/stretching exercises"""
        return self.search_exercises(
            db=db,
            style='Stretches',
            muscle_groups=[muscle_focus] if muscle_focus else None,
            limit=limit
        )
    
    def search_by_muscle_group(self, db: Session, muscle_group: str, difficulty: str, 
                               equipment_ids: List[int], limit: int = 30) -> List[Dict]:
        """Search exercises targeting specific muscle group"""
        return self.search_exercises(
            db=db,
            difficulty=difficulty,
            muscle_groups=[muscle_group],
            equipment_ids=equipment_ids,
            limit=limit
        )


# ─────────────────────────────────────────────
# FARSI WORKOUT PLAN GENERATOR
# ─────────────────────────────────────────────
class FarsiWorkoutPlanGenerator:
    """AI-powered workout plan generator using AvalAI Gemini API for Farsi output"""
    
    def __init__(self, search_engine: FarsiExerciseSearchEngine):
        self.search_engine = search_engine
    
    def generate_weekly_plan(self, db: Session, user_profile: Dict) -> Dict:
        """
        Generate a complete weekly workout plan based on user profile.
        
        Args:
            db: SQLAlchemy database session
            user_profile: Dictionary containing:
                - user_id: User identifier
                - age: User age
                - weight: User weight (kg)
                - height: User height (cm)
                - gender: User gender
                - workout_goal_id: Workout goal ID
                - physical_fitness: Fitness level (beginner, intermediate, advanced, expert)
                - fitness_days: Number of training days per week (1-7)
                - workout_limitations: Any physical limitations or injuries
                - specialized_sport: Sport-specific training requirements
                - training_location: Training location (home, gym, outdoor)
                - equipment_ids: Available equipment IDs list
                
        Returns:
            Complete workout plan with weekly structure in Farsi
        """
        # Extract user profile details
        age = user_profile.get('age', 30)
        weight = float(user_profile.get('weight', 70))
        height = float(user_profile.get('height', 170))
        gender = user_profile.get('gender', 'male')
        physical_fitness = user_profile.get('physical_fitness', 'beginner')
        fitness_days = user_profile.get('fitness_days', 3)
        limitations = user_profile.get('workout_limitations', 'بدون محدودیت')
        specialized_sport = user_profile.get('specialized_sport', 'ندارد')
        location = user_profile.get('training_location', 'home')
        equipment_ids = user_profile.get('equipment_ids', [1])  # 1 = Bodyweight
        
        # Get workout goal info
        goal_label = "تناسب اندام عمومی"
        goal_description = ""
        if user_profile.get('workout_goal_id'):
            goal_query = text("""
                SELECT goal_label_fa, description_fa 
                FROM workout_goals 
                WHERE workout_goal_id = :goal_id
            """)
            goal_result = db.execute(goal_query, {'goal_id': user_profile['workout_goal_id']}).fetchone()
            if goal_result:
                goal_label = goal_result[0] or goal_label
                goal_description = goal_result[1] or ""
        
        # Map fitness level to difficulty
        difficulty_mapping = {
            'beginner': 'Beginner',
            'intermediate': 'Novice',
            'advanced': 'Intermediate',
            'expert': 'Advanced'
        }
        difficulty = difficulty_mapping.get(physical_fitness.lower(), 'Beginner')
        
        # Get equipment names in Farsi
        equipment_names = []
        if equipment_ids:
            eq_query = text("""
                SELECT name_fa FROM equipment WHERE equipment_id = ANY(:ids)
            """)
            eq_result = db.execute(eq_query, {'ids': equipment_ids})
            equipment_names = [row[0] for row in eq_result.fetchall()]
        
        print(f"🎯 در حال تولید برنامه تمرینی برای: {user_profile.get('user_id', 'کاربر ناشناس')}")
        print(f"   هدف: {goal_label} | سطح: {physical_fitness} | روزهای تمرین: {fitness_days}")
        print(f"   سختی: {difficulty} | تجهیزات: {', '.join(equipment_names[:3])}...")
        
        # Define muscle groups based on training days
        weekly_split = self._generate_weekly_split(fitness_days, goal_label)
        
        # Search for exercises for each day
        print("\n🔍 جستجوی تمرینات از پایگاه داده...")
        daily_exercises = []
        for day_info in weekly_split:
            exercises = self._search_exercises_for_day(
                db, day_info, difficulty, equipment_ids
            )
            daily_exercises.append({
                'day_info': day_info,
                'exercises': exercises
            })
        
        # Generate structured plan using AvalAI
        print("\n🤖 تولید برنامه ساختاریافته با AvalAI Gemini API...")
        workout_plan = self._generate_plan_with_avalai(
            user_profile, daily_exercises, limitations, difficulty,
            goal_label, goal_description, equipment_names
        )
        
        print("✅ تولید برنامه تمرینی کامل شد!\n")
        
        return workout_plan
    
    def _generate_weekly_split(self, training_days: int, goal_label: str) -> List[Dict]:
        """Generate weekly training split with specific muscle targets"""
        
        day_names = ["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه"]
        
        if training_days <= 3:
            # Full body workouts
            split = [
                {'day_name': day_names[i], 'focus': 'تمرین تمام بدن', 'muscle_groups': ['Chest', 'Back', 'Legs', 'Shoulders', 'Arms']}
                for i in range(training_days)
            ]
        elif training_days == 4:
            split = [
                {'day_name': day_names[0], 'focus': 'بالاتنه (فشاری)', 'muscle_groups': ['Chest', 'Shoulders', 'Arms']},
                {'day_name': day_names[1], 'focus': 'پایین تنه', 'muscle_groups': ['Legs', 'Glutes', 'Calves']},
                {'day_name': day_names[2], 'focus': 'بالاتنه (کششی)', 'muscle_groups': ['Back', 'Arms']},
                {'day_name': day_names[4], 'focus': 'تمام بدن', 'muscle_groups': ['Chest', 'Back', 'Legs', 'Core']}
            ]
        elif training_days == 5:
            split = [
                {'day_name': day_names[0], 'focus': 'سینه', 'muscle_groups': ['Chest']},
                {'day_name': day_names[1], 'focus': 'پشت', 'muscle_groups': ['Back']},
                {'day_name': day_names[2], 'focus': 'پاها', 'muscle_groups': ['Legs', 'Glutes']},
                {'day_name': day_names[3], 'focus': 'شانه و بازو', 'muscle_groups': ['Shoulders', 'Arms']},
                {'day_name': day_names[5], 'focus': 'کور و کاردیو', 'muscle_groups': ['Core']}
            ]
        else:  # 6-7 days
            split = [
                {'day_name': day_names[0], 'focus': 'سینه', 'muscle_groups': ['Chest']},
                {'day_name': day_names[1], 'focus': 'پشت', 'muscle_groups': ['Back']},
                {'day_name': day_names[2], 'focus': 'پاها', 'muscle_groups': ['Legs']},
                {'day_name': day_names[3], 'focus': 'شانه', 'muscle_groups': ['Shoulders']},
                {'day_name': day_names[4], 'focus': 'بازو', 'muscle_groups': ['Arms']},
                {'day_name': day_names[5], 'focus': 'کور', 'muscle_groups': ['Core']}
            ]
            if training_days == 7:
                split.append({'day_name': day_names[6], 'focus': 'ریکاوری فعال', 'muscle_groups': []})
        
        return split[:training_days]
    
    def _search_exercises_for_day(self, db: Session, day_info: Dict, difficulty: str,
                                  equipment_ids: List[int]) -> Dict:
        """Search for exercises for a specific training day"""
        
        muscle_groups = day_info['muscle_groups']
        focus = day_info['focus']
        
        # Search warmup exercises
        warmup_muscle = muscle_groups[0] if muscle_groups else None
        warmup_exercises = self.search_engine.search_warmup_exercises(
            db=db,
            muscle_focus=warmup_muscle,
            equipment_ids=equipment_ids,
            limit=10
        )
        
        # Search main exercises by muscle groups
        main_exercises = []
        seen_ids = set()
        
        for muscle in muscle_groups:
            exercises = self.search_engine.search_by_muscle_group(
                db=db,
                muscle_group=muscle,
                difficulty=difficulty,
                equipment_ids=equipment_ids,
                limit=15
            )
            
            # Add unique exercises
            for ex in exercises:
                if ex['exercise_id'] not in seen_ids:
                    main_exercises.append(ex)
                    seen_ids.add(ex['exercise_id'])
        
        # Search cooldown exercises
        cooldown_muscle = muscle_groups[0] if muscle_groups else None
        cooldown_exercises = self.search_engine.search_cooldown_exercises(
            db=db,
            muscle_focus=cooldown_muscle,
            limit=10
        )
        
        return {
            'warmup': warmup_exercises[:10],
            'main': main_exercises[:30],
            'cooldown': cooldown_exercises[:10]
        }
    
    def _generate_plan_with_avalai(self, user_profile: Dict, daily_exercises: List[Dict],
                                   limitations: str, difficulty: str, goal_label: str,
                                   goal_description: str, equipment_names: List[str]) -> Dict:
        """Use AvalAI Gemini API to structure the workout plan in Farsi"""
        
        # Prepare the prompt in Farsi
        system_instructions = f"""
شما یک مربی تناسب اندام حرفه‌ای هستید که برنامه‌های تمرینی شخصی‌سازی شده به زبان فارسی تولید می‌کنید.

اطلاعات کاربر:
- سن: {user_profile.get('age', 30)} سال
- وزن: {user_profile.get('weight', 70)} کیلوگرم
- قد: {user_profile.get('height', 170)} سانتی‌متر
- جنسیت: {user_profile.get('gender', 'male')}
- سطح آمادگی: {user_profile.get('physical_fitness', 'beginner')}
- هدف: {goal_label}
{f"- توضیحات هدف: {goal_description}" if goal_description else ""}
- محدودیت‌ها: {limitations}
- تجهیزات موجود: {', '.join(equipment_names) if equipment_names else 'وزن بدن'}
- محل تمرین: {user_profile.get('training_location', 'home')}

وظیفه شما:
1. تولید یک استراتژی کلی برنامه تمرینی به زبان فارسی (2-3 پاراگراف)
2. توضیح انتظارات و نتایج مورد انتظار (2-3 پاراگراف)
3. برای هر روز تمرینی، از تمرینات ارائه شده، 4-6 تمرین مناسب انتخاب کنید
4. برای هر تمرین، ست، تکرار، تمپو، و استراحت مشخص کنید
5. برای گرم کردن، از تمرینات warmup استفاده کنید
6. برای سرد کردن، از تمرینات cooldown استفاده کنید

نکات مهم:
- همه خروجی‌ها باید به زبان فارسی باشد
- تمرینات را بر اساس سطح کاربر و هدف او انتخاب کنید
- برنامه باید متوازن و جامع باشد
- توجه به محدودیت‌های کاربر داشته باشید
"""

        # Create user message with exercise data
        exercises_data = []
        for day_data in daily_exercises:
            day_info = day_data['day_info']
            exercises = day_data['exercises']
            
            exercises_data.append({
                'day_name': day_info['day_name'],
                'focus': day_info['focus'],
                'warmup_exercises': [
                    {
                        'exercise_id': ex['exercise_id'],
                        'name_fa': ex['name_fa'],
                        'difficulty_fa': ex['difficulty_fa']
                    } for ex in exercises['warmup']
                ],
                'main_exercises': [
                    {
                        'exercise_id': ex['exercise_id'],
                        'name_fa': ex['name_fa'],
                        'difficulty_fa': ex['difficulty_fa'],
                        'muscle_names': ex['muscle_names']
                    } for ex in exercises['main']
                ],
                'cooldown_exercises': [
                    {
                        'exercise_id': ex['exercise_id'],
                        'name_fa': ex['name_fa'],
                        'difficulty_fa': ex['difficulty_fa']
                    } for ex in exercises['cooldown']
                ]
            })
        
        user_message = f"""
لطفاً یک برنامه تمرینی یک هفته‌ای کامل تولید کنید.

تمرینات موجود برای هر روز:
{json.dumps(exercises_data, ensure_ascii=False, indent=2)}

خروجی را به صورت JSON با فرمت زیر ارائه دهید:
{{
  "strategy": "استراتژی کلی برنامه تمرینی به زبان فارسی...",
  "expectations": "انتظارات و نتایج مورد انتظار به زبان فارسی...",
  "days": [
    {{
      "day_name": "شنبه",
      "focus": "تمرین تمام بدن",
      "warmup": "توضیحات گرم کردن",
      "cooldown": "توضیحات سرد کردن",
      "exercises": [
        {{
          "exercise_id": 123,
          "exercise_order": 1,
          "sets": "3",
          "reps": "10-12",
          "tempo": "2-0-2-0",
          "rest": "60 ثانیه",
          "notes": "یادداشت‌های اضافی به فارسی"
        }}
      ]
    }}
  ]
}}

نکات مهم:
- exercise_id باید همان شناسه تمرینی باشد که در لیست تمرینات موجود ارائه شده است
- exercise_order نشان‌دهنده ترتیب اجرای تمرینات است (1، 2، 3، ...)
- حتماً از تمرینات موجود در لیست استفاده کنید

فقط JSON را برگردانید، بدون توضیحات اضافی.
"""

        # Call AvalAI API
        try:
            response_text = self._call_avalai_api(system_instructions, user_message)
            workout_data = self._parse_json_response(response_text)
            
            # Validate and return
            if workout_data and 'strategy' in workout_data and 'expectations' in workout_data and 'days' in workout_data:
                # Validate that all exercises have valid exercise_ids
                valid = True
                for day in workout_data.get('days', []):
                    for exercise in day.get('exercises', []):
                        if not exercise.get('exercise_id'):
                            print(f"⚠️ تمرین بدون exercise_id یافت شد در روز {day.get('day_name')}")
                            valid = False
                            break
                    if not valid:
                        break
                
                if valid:
                    return workout_data
                else:
                    print("⚠️ پاسخ نامعتبر از AI (exercise_id موجود نیست)، استفاده از برنامه پیش‌فرض...")
                    return self._generate_fallback_plan(daily_exercises)
            else:
                print("⚠️ پاسخ نامعتبر از AI، استفاده از برنامه پیش‌فرض...")
                return self._generate_fallback_plan(daily_exercises)
                
        except Exception as e:
            print(f"❌ خطا در تولید برنامه با AvalAI: {e}")
            return self._generate_fallback_plan(daily_exercises)
    
    def _call_avalai_api(self, system_instructions: str, user_message: str, 
                         max_retries: int = 3) -> str:
        """Call AvalAI Gemini API with retry logic"""
        
        url = f"{AVALAI_BASE_URL}/v1beta/models/{GEMINI_MODEL}:generateContent"
        
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": AVALAI_API_KEY
        }
        
        payload = {
            "system_instruction": {
                "parts": [{"text": system_instructions}]
            },
            "contents": [
                {
                    "parts": [{"text": user_message}]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 8192,
                "responseMimeType": "application/json"
            }
        }
        
        for attempt in range(max_retries):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=60)
                response.raise_for_status()
                
                data = response.json()
                
                if 'candidates' in data and len(data['candidates']) > 0:
                    content = data['candidates'][0].get('content', {})
                    parts = content.get('parts', [])
                    if parts and 'text' in parts[0]:
                        return parts[0]['text']
                
                raise ValueError("Invalid response format from AvalAI API")
                
            except requests.exceptions.RequestException as e:
                print(f"❌ تلاش {attempt + 1}/{max_retries} ناموفق: {e}")
                if attempt == max_retries - 1:
                    raise
        
        raise Exception("Failed to get response from AvalAI API after retries")
    
    def _parse_json_response(self, response_text: str) -> Dict:
        """Parse JSON response from AvalAI API"""
        try:
            # Try direct JSON parse
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            if '```json' in response_text:
                start = response_text.find('```json') + 7
                end = response_text.find('```', start)
                json_text = response_text[start:end].strip()
                return json.loads(json_text)
            elif '```' in response_text:
                start = response_text.find('```') + 3
                end = response_text.find('```', start)
                json_text = response_text[start:end].strip()
                return json.loads(json_text)
            else:
                raise ValueError("Could not extract JSON from response")
    
    def _generate_fallback_plan(self, daily_exercises: List[Dict]) -> Dict:
        """Generate a simple fallback plan if AI fails"""
        
        days = []
        for day_data in daily_exercises:
            day_info = day_data['day_info']
            exercises = day_data['exercises']
            
            # Select 4-6 main exercises
            selected_exercises = exercises['main'][:5]
            
            day_exercises = []
            for i, ex in enumerate(selected_exercises, 1):
                day_exercises.append({
                    'exercise_id': ex['exercise_id'],
                    'sets': '3',
                    'reps': '10-12',
                    'tempo': '2-0-2-0',
                    'rest': '60 ثانیه',
                    'notes': f"تمرین {ex['name_fa']}",
                    'exercise_order': i
                })
            
            days.append({
                'day_name': day_info['day_name'],
                'focus': day_info['focus'],
                'warmup': '5-10 دقیقه کشش پویا و حرکات آماده‌سازی',
                'cooldown': '5-10 دقیقه کشش ایستا و فوم رولر',
                'exercises': day_exercises
            })
        
        return {
            'strategy': 'این برنامه تمرینی بر اساس اطلاعات پروفایل شما طراحی شده است. رویکرد این برنامه ترکیبی از تمرینات قدرتی و هوازی است که به صورت پیشرونده شدت پیدا می‌کند.',
            'expectations': 'با انجام منظم این برنامه، افزایش قدرت، استقامت و تناسب اندام کلی را تجربه خواهید کرد.',
            'days': days
        }


# ─────────────────────────────────────────────
# MAIN API FUNCTION
# ─────────────────────────────────────────────
def generate_farsi_workout_plan(db: Session, user_profile: Dict) -> Dict:
    """
    Main function to generate a Farsi workout plan using AvalAI API.
    
    Args:
        db: SQLAlchemy database session
        user_profile: User profile dictionary containing:
            - user_id, age, weight, height, gender
            - workout_goal_id, physical_fitness, fitness_days
            - workout_limitations, specialized_sport
            - training_location, equipment_ids
            
    Returns:
        Complete workout plan dictionary with strategy, expectations, and daily exercises
    """
    # Initialize components
    search_engine = FarsiExerciseSearchEngine()
    plan_generator = FarsiWorkoutPlanGenerator(search_engine)
    
    # Generate the plan
    result = plan_generator.generate_weekly_plan(db, user_profile)
    
    return result
