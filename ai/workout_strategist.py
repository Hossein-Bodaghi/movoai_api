"""
AI Workout Strategy Generator using AvalAI API
Generates comprehensive 12-week training strategies based on user profile
"""
import os
import json
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
AVALAI_BASE_URL = "https://api.avalai.ir"
AVALAI_API_KEY = os.getenv("x-goog-api-key")

if not AVALAI_API_KEY:
    raise ValueError("x-goog-api-key not found in .env file")

# Gemini model configuration
# GEMINI_MODEL = "gemini-2.5-pro"
GEMINI_MODEL = "gemini-3-flash-preview"
# GEMINI_MODEL = "gemini-2.5-flash-lite"
# GEMINI_MODEL = "gemini-2.5-flash"

# ─────────────────────────────────────────────
# DATABASE MUSCLE GROUPS & REGIONS
# ─────────────────────────────────────────────

# Muscle Groups (from workout_db.muscle_group table)
# Distribution: Glutes (20.54%), Arms (16.56%), Back (14.74%), Quads (13.32%)
MUSCLE_GROUPS = {
    1: {"name_en": "Arms", "name_fa": "بازو", "percentage": 16.56},
    2: {"name_en": "Back", "name_fa": "پشت", "percentage": 14.74},
    3: {"name_en": "Calves", "name_fa": "ساق پا", "percentage": 3.93},
    4: {"name_en": "Chest", "name_fa": "سینه", "percentage": 5.92},
    5: {"name_en": "Core", "name_fa": "شکم", "percentage": 8.73},
    6: {"name_en": "Feet", "name_fa": "کف پا", "percentage": 0.43},
    7: {"name_en": "Glutes", "name_fa": "سرینی (باسن)", "percentage": 20.54},
    8: {"name_en": "Hamstrings", "name_fa": "همسترینگ (پشت پا)", "percentage": 5.62},
    9: {"name_en": "Neck", "name_fa": "گردن", "percentage": 0.30},
    10: {"name_en": "Quads", "name_fa": "چهارسر ران", "percentage": 13.32},
    11: {"name_en": "Shoulders", "name_fa": "سرشانه", "percentage": 9.90}
}

# Muscle Regions (from workout_db.muscle_region table)
# 38 specific muscle regions mapped to muscle groups
MUSCLE_REGIONS = {
    # Glutes (muscle_group_id: 7)
    1: {"muscle_group_id": 7, "name_en": "Maximus", "name_fa": "سرینی بزرگ"},
    2: {"muscle_group_id": 7, "name_en": "Medius", "name_fa": "سرینی میانی"},
    
    # Quads (muscle_group_id: 10)
    3: {"muscle_group_id": 10, "name_en": "Inner (Vastus Medialis)", "name_fa": "بخش داخلی چهارسر"},
    4: {"muscle_group_id": 10, "name_en": "Outer (Vastus Lateralis)", "name_fa": "بخش خارجی چهارسر"},
    5: {"muscle_group_id": 10, "name_en": "Rectus Femoris", "name_fa": "راست رانی (بخشی از چهارسر)"},
    36: {"muscle_group_id": 10, "name_en": "Adductors", "name_fa": "کشاله ران"},
    
    # Hamstrings (muscle_group_id: 8)
    6: {"muscle_group_id": 8, "name_en": "Lateral (Biceps Femoris)", "name_fa": "بخش خارجی همسترینگ"},
    7: {"muscle_group_id": 8, "name_en": "Medial (Semitendinosus/Semimembranosus)", "name_fa": "بخش داخلی همسترینگ"},
    
    # Calves (muscle_group_id: 3)
    8: {"muscle_group_id": 3, "name_en": "Gastrocnemius", "name_fa": "دوقلو (ساق پا)"},
    9: {"muscle_group_id": 3, "name_en": "Soleus", "name_fa": "نعلی (ساق پا)"},
    10: {"muscle_group_id": 3, "name_en": "Tibialis Anterior", "name_fa": "درشتنئی پیشین"},
    
    # Chest (muscle_group_id: 4)
    11: {"muscle_group_id": 4, "name_en": "Upper (Clavicular)", "name_fa": "بالای سینه"},
    12: {"muscle_group_id": 4, "name_en": "Mid/Lower (Sternal)", "name_fa": "اواسط و پایین سینه"},
    
    # Shoulders (muscle_group_id: 11)
    13: {"muscle_group_id": 11, "name_en": "Anterior Deltoid", "name_fa": "دلتوئید قدامی"},
    14: {"muscle_group_id": 11, "name_en": "Lateral Deltoid", "name_fa": "دلتوئید جانبی"},
    15: {"muscle_group_id": 11, "name_en": "Posterior Deltoid", "name_fa": "دلتوئید خلفی"},
    
    # Back (muscle_group_id: 2)
    16: {"muscle_group_id": 2, "name_en": "Upper Trapezius (General)", "name_fa": "کول (ذوزنقهای)"},
    17: {"muscle_group_id": 2, "name_en": "Upper Trapezius", "name_fa": "بخش بالایی کول"},
    18: {"muscle_group_id": 2, "name_en": "Mid Trapezius / Rhomboids", "name_fa": "بخش میانی کول"},
    19: {"muscle_group_id": 2, "name_en": "Lower Trapezius", "name_fa": "بخش پایینی کول"},
    20: {"muscle_group_id": 2, "name_en": "Latissimus Dorsi", "name_fa": "زیر بغل (پشتی بزرگ)"},
    21: {"muscle_group_id": 2, "name_en": "Erector Spinae", "name_fa": "فیله کمر"},
    22: {"muscle_group_id": 2, "name_en": "General", "name_fa": "عمومی"},
    
    # Arms (muscle_group_id: 1)
    23: {"muscle_group_id": 1, "name_en": "Biceps – Long Head", "name_fa": "سر بلند جلو بازو"},
    24: {"muscle_group_id": 1, "name_en": "Biceps – Short Head", "name_fa": "سر کوتاه جلو بازو"},
    25: {"muscle_group_id": 1, "name_en": "Triceps – Long Head", "name_fa": "سر بلند پشت بازو"},
    26: {"muscle_group_id": 1, "name_en": "Triceps – Lateral Head", "name_fa": "سر جانبی پشت بازو"},
    27: {"muscle_group_id": 1, "name_en": "Triceps – Medial Head", "name_fa": "سر میانی پشت بازو"},
    28: {"muscle_group_id": 1, "name_en": "Forearm (General)", "name_fa": "ساعد"},
    29: {"muscle_group_id": 1, "name_en": "Forearm – Flexors", "name_fa": "تاکنندههای مچ"},
    30: {"muscle_group_id": 1, "name_en": "Forearm – Extensors", "name_fa": "بازکنندههای مچ"},
    31: {"muscle_group_id": 1, "name_en": "Intrinsic Hand Muscles", "name_fa": "پنجه / دستها"},
    
    # Core (muscle_group_id: 5)
    32: {"muscle_group_id": 5, "name_en": "Rectus Abdominis (General)", "name_fa": "شکم"},
    33: {"muscle_group_id": 5, "name_en": "Upper Rectus Abdominis", "name_fa": "بالای شکم"},
    34: {"muscle_group_id": 5, "name_en": "Lower Rectus Abdominis", "name_fa": "زیر شکم"},
    35: {"muscle_group_id": 5, "name_en": "Obliques", "name_fa": "مورب شکمی"},
    
    # Feet (muscle_group_id: 6)
    37: {"muscle_group_id": 6, "name_en": "Intrinsic Foot Muscles", "name_fa": "کف پا"},
    
    # Neck (muscle_group_id: 9)
    38: {"muscle_group_id": 9, "name_en": "Cervical Muscles", "name_fa": "گردن"}
}

# Allowed Exercise Styles (from workout_db.style table)
# AI can only use these 4 styles for workout planning
ALLOWED_STYLES = {
    5: {"name_en": "Cardio", "name_fa": "کاردیو", "count": 46},
    11: {"name_en": "Recovery", "name_fa": "ریکاوری", "count": 176},
    13: {"name_en": "Stretches", "name_fa": "کشش", "count": 52},
    15: {"name_en": "Yoga", "name_fa": "یوگا", "count": 73}
}


# ─────────────────────────────────────────────
# FARSI WORKOUT STRATEGIST
# ─────────────────────────────────────────────
class FarsiWorkoutStrategist:
    """
    AI-powered workout strategist using AvalAI Gemini API.
    Generates comprehensive 12-week training strategies.
    """
    
    def __init__(self):
        self.api_key = AVALAI_API_KEY
        self.base_url = AVALAI_BASE_URL
        self.model = GEMINI_MODEL
    
    def generate_strategy(self, user_profile: Dict) -> Dict[str, str]:
        """
        Generate a comprehensive 12-week training strategy.
        
        Args:
            user_profile: Dictionary containing:
                - user_id: User identifier
                - age: User age
                - weight: User weight (kg)
                - height: User height (cm)
                - gender: User gender
                - workout_goal_id: Training goal ID (1-20)
                - physical_fitness: Fitness level (beginner/intermediate/advanced/expert)
                - fitness_days: Number of fitness training days per week (0-7)
                - sport: Current sport/activity (if any)
                - sport_days: Number of sport training days per week (0-7)
                - focus: User's focus and priorities
                - workout_limitations: Physical limitations or injuries
                - training_location: Training location (home/gym/outdoor)
                - equipment_ids: Available equipment list
                
        Returns:
            Dictionary with three outputs:
            {
                "detailed_strategy": "Technical 12-week strategy for Plan Generator AI",
                "user_summary": "User-friendly concise explanation",
                "expectations": "Realistic outcomes and milestones"
            }
        """
        # Extract user profile details
        age = user_profile.get('age', 30)
        weight = user_profile.get('weight', 70)
        height = user_profile.get('height', 170)
        gender = user_profile.get('gender', 'male')
        fitness_level = user_profile.get('physical_fitness', 'beginner')
        fitness_days = user_profile.get('fitness_days', 3)
        sport = user_profile.get('sport', 'ندارد')
        sport_days = user_profile.get('sport_days', 0)
        focus = user_profile.get('focus', 'ندارد')
        limitations = user_profile.get('workout_limitations', 'بدون محدودیت')
        location = user_profile.get('training_location', 'home')
        
        # Map workout goal ID to Persian goal name
        goal_mapping = {
            1: 'افزایش قدرت و توان',
            2: 'بهبود سرعت و چابکی',
            3: 'افزایش استقامت و پایداری',
            4: 'افزایش انعطاف‌پذیری و تحرک',
            5: 'بهینه‌سازی بازیابی و انعطاف‌پذیری',
            6: 'افزایش توده عضلانی بدون چربی',
            7: 'سوزاندن چربی با حفظ عضله',
            8: 'بهبود تعریف و تن عضلانی',
            9: 'تغییر کلی فیزیک بدن',
            10: 'هدف‌گیری مناطق مشکل‌دار خاص',
            11: 'حداکثر نتایج در کمترین زمان',
            12: 'حفظ سطح فعلی تناسب اندام',
            13: 'تعادل بین تناسب اندام و زندگی شلوغ',
            14: 'ایجاد قدرت کاربردی روزانه',
            15: 'تمرین کم‌فشار اما مؤثر',
            16: 'بازیابی از آسیب یا جراحی',
            17: 'بازیابی سطح از دست رفته تناسب اندام',
            18: 'تقویت مناطق ضعیف یا نامتعادل',
            19: 'جلوگیری از آسیب مجدد و ایجاد مقاومت',
            20: 'پیشرفت تدریجی و ایمن'
        }
        goal_id = user_profile.get('workout_goal_id', 12)
        goal = goal_mapping.get(goal_id, 'حفظ سطح فعلی تناسب اندام')
        
        # Map fitness level to Persian
        fitness_mapping = {
            'beginner': 'مبتدی',
            'intermediate': 'متوسط',
            'advanced': 'پیشرفته',
            'expert': 'حرفه‌ای'
        }
        fitness_fa = fitness_mapping.get(fitness_level.lower(), 'مبتدی')
        
        # Map location to Persian
        location_mapping = {
            'home': 'خانه',
            'gym': 'باشگاه',
            'outdoor': 'فضای باز'
        }
        location_fa = location_mapping.get(location, 'خانه')
        
        # Prepare system instructions
        system_instructions = """شما یک استراتژیست حرفه‌ای تناسب اندام و مربی ورزشی با سال‌ها تجربه هستید.
وظیفه شما طراحی استراتژی جامع و حرفه‌ای برای برنامه تمرینی ۱۲ هفته‌ای است.

مسئولیت‌های شما:
1. تحلیل دقیق پروفایل کاربر (سن، وزن، قد، جنسیت، سطح آمادگی، هدف)
2. در نظر گرفتن ورزش فعلی کاربر و روزهای تمرین ورزشی (اگر دارد)
3. طراحی استراتژی ۱۲ هفته‌ای با فازبندی منطقی
4. در نظر گرفتن پیشرفت تدریجی (Progressive Overload)
5. توجه به دوره‌های ریکاوری و Deload
6. تطبیق برنامه با تجهیزات موجود و محدودیت‌های کاربر
7. هماهنگی برنامه با فوکوس و اولویت‌های کاربر

اطلاعات گروه‌های عضلانی موجود در پایگاه داده:
- Glutes (سرینی): 20.54% تمرینات - شامل Maximus، Medius
- Arms (بازو): 16.56% تمرینات - شامل Biceps (Long/Short Head)، Triceps (Long/Lateral/Medial Head)، Forearms
- Back (پشت): 14.74% تمرینات - شامل Trapezius، Latissimus Dorsi، Erector Spinae، Rhomboids
- Quads (چهارسر): 13.32% تمرینات - شامل Vastus Medialis/Lateralis، Rectus Femoris، Adductors
- Shoulders (سرشانه): 9.90% تمرینات - شامل Anterior/Lateral/Posterior Deltoid
- Core (شکم): 8.73% تمرینات - شامل Rectus Abdominis (Upper/Lower)، Obliques
- Chest (سینه): 5.92% تمرینات - شامل Upper (Clavicular)، Mid/Lower (Sternal)
- Hamstrings (همسترینگ): 5.62% تمرینات - شامل Biceps Femoris، Semitendinosus/Semimembranosus
- Calves (ساق پا): 3.93% تمرینات - شامل Gastrocnemius، Soleus، Tibialis Anterior
- Feet (کف پا): 0.43% تمرینات
- Neck (گردن): 0.30% تمرینات

سبک‌های تمرینی مجاز (محدود به ۴ نوع):
- Recovery (ریکاوری): 176 تمرین - فعالیت‌های بازیابی و استراحت فعال
- Yoga (یوگا): 73 تمرین - انعطاف‌پذیری و تمرکز ذهنی
- Stretches (کشش): 52 تمرین - کشش‌های دینامیک و استاتیک
- Cardio (کاردیو): 46 تمرین - تمرینات قلبی-عروقی

محدودیت‌های مهم:
- از فیلتر کردن بر اساس Goal (هدف تمرین) استفاده نکنید - این موارد ذاتی انتخاب تمرین هستند
- از فیلتر کردن بر اساس Mechanics (مکانیک تمرین) استفاده نکنید - این موارد ذاتی تمرینات هستند
- از فیلتر کردن بر اساس Position (وضعیت بدن) استفاده نکنید - این موارد ذاتی تمرینات هستند
- از فیلتر کردن بر اساس Training Phase استفاده نکنید - این توسط ساختار برنامه تعیین می‌شود

خروجی شما باید شامل ۳ بخش مجزا باشد:

1. detailed_strategy: استراتژی تکنیکال و دقیق برای هوش مصنوعی برنامه‌ریز هفتگی
   - فازبندی دقیق هر ۱۲ هفته (مثلاً هفته ۱-۴: فاز آشنایی، هفته ۵-۸: فاز رشد)
   - برای هر فاز مشخص کنید: تمرکز اصلی، نوع تفکیک عضلانی (Full Body/Upper-Lower/PPL)
   - شدت تمرینات (درصد 1RM یا سطح سختی)
   - حجم تمرینات (تعداد ست و تکرار)
   - روش‌های پیشرفت (افزایش وزن، تکرار، ست)
   - زمان استراحت بین ست‌ها
   - این بخش برای AI است، پس تکنیکال و دقیق باشد (حداقل ۲۰۰ کاراکتر)

2. user_summary: خلاصه مختصر و کاربرپسند برای نمایش به کاربر
   - توضیح ساده فازهای برنامه
   - آنچه کاربر در هر فاز انتظار دارد
   - نکات مهم برای موفقیت
   - این بخش برای کاربر است، پس ساده و انگیزه‌بخش باشد (۵۰-۵۰۰ کاراکتر)

3. expectations: انتظارات واقع‌بینانه و مثبت
   - نتایج قابل انتظار در ۱۲ هفته (بر اساس هدف)
   - نقاط عطف (Milestones) در طول برنامه
   - تغییرات جسمانی، قدرت، استقامت
   - زمان‌بندی تغییرات (مثلاً از هفته ۶ تغییرات ظاهری)
   - واقع‌بینانه و مثبت باشد (۵۰-۵۰۰ کاراکتر)

قوانین فرمت متن:
- از متن ساده فارسی استفاده کنید
- برای جدا کردن بخش‌ها از خط جدید استفاده کنید
- برای لیست‌ها از - در ابتدای خط استفاده کنید
- متن باید خواناتر و ساده باشد

مهم: خروجی باید حتماً JSON معتبر باشد با این ساختار دقیق:
{
  "detailed_strategy": "متن فارسی دقیق و تکنیکال بدون علامت markdown...",
  "user_summary": "متن فارسی ساده و کاربرپسند بدون علامت markdown...",
  "expectations": "متن فارسی انتظارات واقع‌بینانه بدون علامت markdown..."
}
"""
        
        # Prepare user message
        user_message = f"""لطفاً برای کاربر زیر یک استراتژی جامع ۱۲ هفته‌ای طراحی کنید:

**اطلاعات کاربر:**
- سن: {age} سال
- وزن: {weight} کیلوگرم
- قد: {height} سانتی‌متر
- جنسیت: {gender}
- سطح آمادگی: {fitness_fa}
- هدف تمرینی: {goal}
- فوکوس و اولویت: {focus}
- ورزش فعلی: {sport}
- روزهای تمرین ورزشی در هفته: {sport_days} روز
- روزهای تمرین تناسب اندام در هفته: {fitness_days} روز
- محدودیت‌های جسمی: {limitations}
- مکان تمرین: {location_fa}

**الزامات:**
1. استراتژی باید ۱۲ هفته‌ای باشد
2. فازبندی منطقی داشته باشد (مثلاً ۳ فاز ۴ هفته‌ای)
3. پیشرفت تدریجی (Progressive Overload) رعایت شود
4. دوره‌های ریکاوری در نظر گرفته شود
5. متناسب با سطح آمادگی کاربر باشد

**خروجی مورد نیاز:**
یک JSON معتبر با ۳ فیلد: detailed_strategy، user_summary، expectations

فقط JSON را برگردانید، بدون توضیحات اضافی."""

        # Call AvalAI API
        response_text = self._call_avalai_api(system_instructions, user_message)
        
        # Parse JSON response
        strategy_data = self._parse_json_response(response_text)
        
        # Clean markdown symbols from all text fields
        strategy_data = self._clean_markdown(strategy_data)
        
        # Validate output
        if not self._validate_strategy(strategy_data):
            print("⚠️  Strategy validation failed, using fallback")
            strategy_data = self._generate_fallback_strategy(user_profile)
        
        return strategy_data
    
    def _call_avalai_api(self, system_instructions: str, user_message: str, 
                         max_retries: int = 3) -> str:
        """
        Call AvalAI Gemini API with retry logic.
        
        Args:
            system_instructions: System prompt for the model
            user_message: User prompt
            max_retries: Maximum number of retry attempts
            
        Returns:
            Response text from the API
        """
        url = f"{self.base_url}/v1beta/models/{self.model}:generateContent"
        
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key
        }
        
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": user_message}]
                }
            ],
            "systemInstruction": {
                "role": "user",
                "parts": [{"text": system_instructions}]
            },
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 8192
            }
        }
        
        for attempt in range(1, max_retries + 1):
            try:
                print(f"📡 Calling AvalAI Strategist API (attempt {attempt}/{max_retries})...")
                
                response = requests.post(url, headers=headers, json=payload, timeout=60)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if 'candidates' in result and len(result['candidates']) > 0:
                        candidate = result['candidates'][0]
                        if 'content' in candidate and 'parts' in candidate['content']:
                            text = candidate['content']['parts'][0]['text']
                            print(f"✅ Strategist API call successful")
                            return text
                    
                    raise Exception("Invalid response structure from AvalAI API")
                
                else:
                    print(f"❌ API call failed with status {response.status_code}: {response.text}")
                    if attempt < max_retries:
                        print(f"🔄 Retrying...")
                        continue
                    else:
                        raise Exception(f"API call failed after {max_retries} attempts")
            
            except requests.Timeout:
                print(f"⏱️  Request timeout (attempt {attempt}/{max_retries})")
                if attempt < max_retries:
                    print(f"🔄 Retrying...")
                    continue
                else:
                    raise Exception(f"Request timeout after {max_retries} attempts")
            
            except Exception as e:
                print(f"❌ Error during API call: {e}")
                if attempt < max_retries:
                    print(f"🔄 Retrying...")
                    continue
                else:
                    raise
        
        raise Exception("Failed to get response from AvalAI API")
    
    def _parse_json_response(self, response_text: str) -> Dict[str, str]:
        """
        Parse JSON response from AvalAI API.
        Handles both raw JSON and markdown-wrapped JSON.
        
        Args:
            response_text: Response text from API
            
        Returns:
            Parsed strategy dictionary
        """
        try:
            # Try direct JSON parsing
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Try extracting JSON from markdown code blocks
            try:
                # Look for ```json ... ``` blocks
                if '```json' in response_text:
                    start = response_text.find('```json') + 7
                    end = response_text.find('```', start)
                    json_str = response_text[start:end].strip()
                    return json.loads(json_str)
                
                # Look for ``` ... ``` blocks
                elif '```' in response_text:
                    start = response_text.find('```') + 3
                    end = response_text.find('```', start)
                    json_str = response_text[start:end].strip()
                    return json.loads(json_str)
                
                else:
                    raise ValueError("No JSON found in response")
            
            except Exception as e:
                print(f"❌ Failed to parse JSON response: {e}")
                raise
    
    def _clean_markdown(self, strategy_data: Dict[str, str]) -> Dict[str, str]:
        """
        Clean markdown symbols from strategy text fields.
        
        Args:
            strategy_data: Strategy dictionary with potential markdown
            
        Returns:
            Cleaned strategy dictionary
        """
        import re
        
        def clean_text(text: str) -> str:
            """Remove markdown formatting from text"""
            if not text:
                return text
            
            # Remove bold/italic markers
            text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # **bold**
            text = re.sub(r'\*([^*]+)\*', r'\1', text)      # *italic*
            text = re.sub(r'__([^_]+)__', r'\1', text)      # __bold__
            text = re.sub(r'_([^_]+)_', r'\1', text)        # _italic_
            
            # Clean up multiple newlines
            text = re.sub(r'\n{3,}', '\n\n', text)  # Max 2 consecutive newlines
            
            # Clean up spacing around newlines
            text = re.sub(r' +\n', '\n', text)  # Remove trailing spaces before newline
            text = re.sub(r'\n +', '\n', text)  # Remove leading spaces after newline
            
            return text.strip()
        
        # Clean all text fields
        cleaned = {}
        for key, value in strategy_data.items():
            if isinstance(value, str):
                cleaned[key] = clean_text(value)
            else:
                cleaned[key] = value
        
        return cleaned
    
    def _validate_strategy(self, strategy_data: Dict[str, str]) -> bool:
        """
        Validate strategy output has all required fields with sufficient content.
        
        Args:
            strategy_data: Strategy dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['detailed_strategy', 'user_summary', 'expectations']
        
        # Check all fields exist
        for field in required_fields:
            if field not in strategy_data:
                print(f"❌ Missing required field: {field}")
                return False
        
        # Check detailed_strategy has sufficient content (min 200 chars)
        if len(strategy_data['detailed_strategy']) < 200:
            print(f"❌ detailed_strategy too short: {len(strategy_data['detailed_strategy'])} chars")
            return False
        
        # Check user_summary is reasonable length (50-500 chars)
        summary_len = len(strategy_data['user_summary'])
        if summary_len < 50 or summary_len > 1000:
            print(f"❌ user_summary length invalid: {summary_len} chars")
            return False
        
        # Check expectations is reasonable length (50-500 chars)
        expect_len = len(strategy_data['expectations'])
        if expect_len < 50 or expect_len > 1000:
            print(f"❌ expectations length invalid: {expect_len} chars")
            return False
        
        print("✅ Strategy validation passed")
        return True
    
    def _generate_fallback_strategy(self, user_profile: Dict) -> Dict[str, str]:
        """
        Generate a fallback strategy if AI fails.
        
        Args:
            user_profile: User profile dictionary
            
        Returns:
            Fallback strategy dictionary
        """
        goal_id = user_profile.get('workout_goal_id', 12)
        fitness_level = user_profile.get('physical_fitness', 'beginner')
        
        # Goal-specific strategies (matching database)
        goal_strategies = {
            1: "افزایش قدرت و توان",
            2: "بهبود سرعت و چابکی",
            3: "افزایش استقامت و پایداری",
            4: "افزایش انعطاف‌پذیری و تحرک",
            5: "بهینه‌سازی بازیابی و انعطاف‌پذیری",
            6: "افزایش توده عضلانی بدون چربی",
            7: "سوزاندن چربی با حفظ عضله",
            8: "بهبود تعریف و تن عضلانی",
            9: "تغییر کلی فیزیک بدن",
            10: "هدف‌گیری مناطق مشکل‌دار خاص",
            11: "حداکثر نتایج در کمترین زمان",
            12: "حفظ سطح فعلی تناسب اندام"
        }
        goal_name = goal_strategies.get(goal_id, "حفظ سطح فعلی تناسب اندام")
        
        fallback = {
            "detailed_strategy": f"""برنامه ۱۲ هفته‌ای استاندارد برای {goal_name}:

هفته ۱-۴: فاز پایه‌سازی و آشنایی
- تمرکز: یادگیری فرم صحیح حرکات پایه
- تفکیک: Full Body یا Upper/Lower Split
- شدت: ۶۰-۷۰٪ ظرفیت (برای {fitness_level})
- حجم: ۳ ست × ۸-۱۲ تکرار
- استراحت: ۶۰-۹۰ ثانیه
- پیشرفت: افزایش ۲.۵-۵٪ وزنه هر هفته یا افزایش ۱-۲ تکرار

هفته ۵-۸: فاز رشد و توسعه
- تمرکز: افزایش حجم و تحریک عضلانی
- تفکیک: Upper/Lower یا Push/Pull/Legs
- شدت: ۷۰-۷۵٪ ظرفیت
- حجم: ۳-۴ ست × ۸-۱۲ تکرار
- استراحت: ۶۰ ثانیه
- پیشرفت: افزایش حجم (اضافه کردن ست یا تکرار)

هفته ۹-۱۲: فاز قدرت و تثبیت
- تمرکز: افزایش قدرت و تثبیت نتایج
- تفکیک: حفظ تفکیک فاز قبل
- شدت: ۷۵-۸۰٪ ظرفیت
- حجم: ۴ ست × ۶-۱۰ تکرار
- استراحت: ۹۰-۱۲۰ ثانیه
- هفته ۱۲: Deload (کاهش ۴۰٪ حجم برای ریکاوری)""",
            
            "user_summary": f"""برنامه شما یک برنامه ۱۲ هفته‌ای جامع برای {goal_name} است که به ۳ فاز تقسیم می‌شود:

🔹 هفته‌های ۱-۴: در این فاز، پایه‌های اصلی را یاد می‌گیرید و بدن شما برای تمرینات سنگین‌تر آماده می‌شود.

🔹 هفته‌های ۵-۸: فاز اصلی رشد و پیشرفت است. در این مرحله حجم و شدت تمرینات افزایش می‌یابد.

🔹 هفته‌های ۹-۱۲: فاز نهایی برای تثبیت نتایج و رسیدن به اوج آمادگی است.

با پیروی از این برنامه، به هدف خود نزدیک خواهید شد.""",
            
            "expectations": f"""با رعایت دقیق این برنامه ۱۲ هفته‌ای، می‌توانید انتظار داشته باشید:

✅ در ۴ هفته اول: احساس انرژی بیشتر، بهبود خواب، یادگیری فرم صحیح حرکات

✅ در هفته‌های ۵-۸: افزایش قدرت قابل توجه، تغییرات اولیه در ترکیب بدن، افزایش استقامت

✅ در هفته‌های ۹-۱۲: تغییرات ظاهری محسوس، افزایش ۲۰-۳۰٪ قدرت در حرکات اصلی، بهبود کلی آمادگی جسمانی

نتایج واقع‌بینانه برای {goal_name}: پیشرفت پایدار و قابل اندازه‌گیری در طول ۱۲ هفته."""
        }
        
        return fallback


# ─────────────────────────────────────────────
# MAIN API FUNCTION
# ─────────────────────────────────────────────
def generate_workout_strategy(user_profile: Dict) -> Dict[str, str]:
    """
    Main function to generate a 12-week workout strategy using AvalAI API.
    
    Args:
        user_profile: User profile dictionary containing:
            - user_id, age, weight, height, gender
            - workout_goal_id (1-20), physical_fitness, fitness_days
            - sport, sport_days, focus
            - workout_limitations, training_location, equipment_ids
            
    Returns:
        Strategy dictionary with three outputs:
        {
            "detailed_strategy": "Technical strategy for Plan Generator",
            "user_summary": "User-friendly summary",
            "expectations": "Realistic outcomes"
        }
    """
    strategist = FarsiWorkoutStrategist()
    return strategist.generate_strategy(user_profile)


# ─────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────
if __name__ == "__main__":
    # Example user profile
    test_profile = {
        "user_id": "test_user_strategy_001",
        "age": 28,
        "weight": 75,
        "height": 175,
        "gender": "male",
        "workout_goal_id": 6,  # افزایش توده عضلانی بدون چربی
        "physical_fitness": "intermediate",
        "fitness_days": 4,
        "sport": "فوتبال",
        "sport_days": 2,
        "focus": "افزایش قدرت پاها و بهبود توان انفجاری",
        "workout_limitations": "بدون محدودیت",
        "training_location": "gym",
        "equipment_ids": [1, 2, 3, 5]  # Bodyweight, Dumbbells, Barbell, Cables
    }
    
    print("=" * 80)
    print("🎯 MOVOKIO WORKOUT STRATEGIST")
    print("=" * 80)
    print(f"\n📋 User Profile:")
    print(f"   ID: {test_profile['user_id']}")
    print(f"   Age: {test_profile['age']} years")
    print(f"   Fitness: {test_profile['physical_fitness']}")
    print(f"   Training Days: {test_profile['fitness_days']}")
    print(f"   Goal ID: {test_profile['workout_goal_id']}")
    print("\n" + "-" * 80 + "\n")
    
    # Generate strategy
    strategy = generate_workout_strategy(test_profile)
    
    # Save to file
    output_file = "workout_strategy_output.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(strategy, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 80)
    print("📊 STRATEGY SUMMARY")
    print("=" * 80)
    
    print("\n🔹 DETAILED STRATEGY (for Plan Generator AI):")
    print(f"   Length: {len(strategy['detailed_strategy'])} characters")
    print(f"   Preview: {strategy['detailed_strategy'][:200]}...")
    
    print("\n🔹 USER SUMMARY:")
    print(f"   {strategy['user_summary']}")
    
    print("\n🔹 EXPECTATIONS:")
    print(f"   {strategy['expectations']}")
    
    print(f"\n✅ Complete strategy saved to: {output_file}")
    print("=" * 80)
