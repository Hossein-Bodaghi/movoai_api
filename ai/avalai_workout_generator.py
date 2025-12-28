"""
AI Workout Plan Generator using AvalAI API and SQL-Based Exercise Database
Generates personalized weekly workout plans based on user profile using AvalAI Gemini API
"""

import os
import json
import psycopg2
import requests
import time
from typing import List, Dict, Any, Optional
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

# Database connection parameters
DB_CONFIG = {
    'dbname': 'workout_db',
    'user': 'postgres',
    'password': '926121008',
    'host': 'localhost',
    'port': '5432'
}

# Gemini model configuration
# GEMINI_MODEL = "gemini-2.5-pro"
GEMINI_MODEL = "gemini-3-flash-preview"
# GEMINI_MODEL = "gemini-2.5-flash-lite"
# GEMINI_MODEL = "gemini-2.5-flash"

# Available equipment (first 17 from database)
AVAILABLE_EQUIPMENT = [
    "Bodyweight",
    "Dumbbells", 
    "Barbell",
    "Kettlebell",
    "Cables",
    "Machine",
    "Resistance Band",
    "Plate",
    "Smith-Machine",
    "Medicine Ball",
    "TRX",
    "Stability Ball (Swiss Ball)",
    "Pull-up Bar",
    "Box (Plyo/Step)",
    "Ring (Gymnastic)",
    "Row Erg Rower",
    "Treadmill"
]

# ─────────────────────────────────────────────
# SQL-BASED EXERCISE SEARCH ENGINE
# ─────────────────────────────────────────────
class SQLExerciseSearchEngine:
    """
    SQL-based search engine for finding relevant exercises using filters.
    Connects to workout_db PostgreSQL database.
    """
    
    def __init__(self, db_config: Dict):
        self.db_config = db_config
    
    def get_connection(self):
        """Create database connection"""
        return psycopg2.connect(
            dbname=self.db_config['dbname'],
            user=self.db_config['user'],
            password=self.db_config['password'],
            host=self.db_config['host'],
            port=self.db_config['port']
        )
    
    def search_exercises(self, 
                        difficulty: Optional[str] = None,
                        muscle_groups: Optional[List[str]] = None,
                        muscle_regions: Optional[List[str]] = None,
                        equipment: Optional[List[str]] = None,
                        goals: Optional[List[str]] = None,
                        mechanics: Optional[List[str]] = None,
                        position: Optional[List[str]] = None,
                        training_phase: Optional[List[str]] = None,
                        style: Optional[List[str]] = None,
                        limit: int = 50) -> List[Dict]:
        """
        Search for exercises using SQL filters with detailed database schema.
        
        DATABASE SCHEMA:
        ----------------
        
        DIFFICULTY TABLE (difficulty):
        - Options: Beginner, Novice, Intermediate, Advanced
        - Distribution: Beginner (37%), Novice (26%), Intermediate (25%), Advanced (11%)
        
        MUSCLE_GROUP TABLE (muscle_group):
        - Options: Glutes, Arms, Back, Quads, Shoulders, Core, Chest, Hamstrings, Calves, Feet, Neck
        - Most common: Glutes (20.5%), Arms (16.6%), Back (14.7%), Quads (13.3%)
        
        MUSCLE_REGION TABLE (muscle_region):
        - Specific regions within muscle groups (37 different regions)
        - Examples: Anterior Deltoid, Erector Spinae, Rectus Abdominis, Latissimus Dorsi, etc.
        - Top regions: Anterior Deltoid (11.3%), Erector Spinae (9.8%), Rectus Abdominis (8.3%)
        
        EQUIPMENT TABLE (equipment):
        - Available: Bodyweight, Dumbbells, Barbell, Kettlebell, Cables, Machine, 
          Resistance Band, Plate, Smith-Machine, Medicine Ball, TRX, 
          Stability Ball (Swiss Ball), Pull-up Bar, Box (Plyo/Step), 
          Ring (Gymnastic), Row Erg Rower, Treadmill
        - Most common: Bodyweight (29.6%), Dumbbells (16%), Barbell (10.3%)
        
        GOAL TABLE (goal):
        - Training objectives like Strength, Hypertrophy, Endurance, Power, Flexibility, etc.
        
        MECHANICS TABLE (mechanics):
        - Options: Compound, Isolation, Dynamic, Static, etc.
        - Determines exercise complexity and joint involvement
        
        POSITION TABLE (position):
        - Body positions: Standing, Seated, Lying, Kneeling, etc.
        - Affects exercise stability and difficulty
        
        TRAINING_PHASE TABLE (training_phase):
        - Workout phases: Warm-up, Main Lift, Accessory, Cool-down, etc.
        
        STYLE TABLE (style):
        - Exercise styles: Recovery, Stretches, Cardio
        - Note: style_id is a direct foreign key in the exercise table (not a junction table)
        - Special categorization for workout types
        
        Args:
            difficulty (str, optional): Difficulty level - USER-PROVIDED
                Options: "Beginner", "Novice", "Intermediate", "Advanced"
            
            muscle_groups (List[str], optional): Target muscle groups - AI-FILTERABLE
                Options: "Glutes", "Arms", "Back", "Quads", "Shoulders", "Core", 
                        "Chest", "Hamstrings", "Calves", "Feet", "Neck"
            
            muscle_regions (List[str], optional): Specific muscle regions - AI-FILTERABLE
                Examples: "Anterior Deltoid", "Latissimus Dorsi", "Rectus Abdominis"
            
            equipment (List[str], optional): Available equipment - USER-PROVIDED
                Options: See AVAILABLE_EQUIPMENT list above (first 17 equipment types)
            
            goals (List[str], optional): Training goals - AI-FILTERABLE
                Examples: "Strength", "Hypertrophy", "Endurance", "Power", "Flexibility"
            
            mechanics (List[str], optional): Exercise mechanics - AI-FILTERABLE
                Options: "Compound", "Isolation", "Dynamic", "Static"
            
            position (List[str], optional): Body positions - AI-FILTERABLE
                Options: "Standing", "Seated", "Lying", "Kneeling", "Prone", "Supine"
            
            training_phase (List[str], optional): Workout phase - AI-FILTERABLE
                Options: "Warm-up", "Main Lift", "Accessory", "Cool-down"
            
            style (List[str], optional): Exercise style - AI-FILTERABLE
                Options: "Recovery", "Stretches", "Cardio"
                Note: style_id is a direct foreign key in exercise table
            
            limit (int): Maximum number of results (default: 50)
            
        Returns:
            List[Dict]: List of exercises with full details including:
                - exercise_id, name, instructions
                - difficulty, equipment, muscle groups/regions
                - goals, mechanics, position, training phase, style
        """
        conn = self.get_connection()
        exercises = []
        
        try:
            with conn.cursor() as cursor:
                # Build dynamic SQL query with all relevant tables
                query = """
                    SELECT DISTINCT
                        e.exercise_id,
                        e.name_en,
                        e.name_fa,
                        e.instructions_en,
                        e.instructions_fa,
                        d.name_en as difficulty_en,
                        STRING_AGG(DISTINCT eq.name_en, ', ') as equipment_en,
                        STRING_AGG(DISTINCT mg.name_en, ', ') as muscle_groups_en,
                        STRING_AGG(DISTINCT mr.name_en, ', ') as muscle_regions_en,
                        STRING_AGG(DISTINCT g.name_en, ', ') as goals_en,
                        STRING_AGG(DISTINCT mech.name_en, ', ') as mechanics_en,
                        STRING_AGG(DISTINCT pos.name_en, ', ') as position_en,
                        STRING_AGG(DISTINCT tp.name_en, ', ') as training_phase_en,
                        s.name_en as style_en
                    FROM exercise e
                    LEFT JOIN difficulty d ON e.difficulty_id = d.difficulty_id
                    LEFT JOIN style s ON e.style_id = s.style_id
                    LEFT JOIN exercise_equipment ee ON e.exercise_id = ee.exercise_id
                    LEFT JOIN equipment eq ON ee.equipment_id = eq.equipment_id
                    LEFT JOIN exercise_muscle_group emg ON e.exercise_id = emg.exercise_id
                    LEFT JOIN muscle_group mg ON emg.muscle_group_id = mg.muscle_group_id
                    LEFT JOIN exercise_muscle_region emr ON e.exercise_id = emr.exercise_id
                    LEFT JOIN muscle_region mr ON emr.muscle_region_id = mr.muscle_region_id
                    LEFT JOIN exercise_goal eg ON e.exercise_id = eg.exercise_id
                    LEFT JOIN goal g ON eg.goal_id = g.goal_id
                    LEFT JOIN exercise_mechanics emech ON e.exercise_id = emech.exercise_id
                    LEFT JOIN mechanics mech ON emech.mechanics_id = mech.mechanics_id
                    LEFT JOIN exercise_position epos ON e.exercise_id = epos.exercise_id
                    LEFT JOIN position pos ON epos.position_id = pos.position_id
                    LEFT JOIN exercise_training_phase etp ON e.exercise_id = etp.exercise_id
                    LEFT JOIN training_phase tp ON etp.phase_id = tp.phase_id
                    WHERE 1=1
                """
                
                params = []
                
                # Add difficulty filter (USER-PROVIDED)
                if difficulty:
                    query += " AND LOWER(d.name_en) = LOWER(%s)"
                    params.append(difficulty)
                
                # Add muscle_group filter (AI-FILTERABLE)
                if muscle_groups:
                    muscle_conditions = []
                    for muscle in muscle_groups:
                        muscle_conditions.append("LOWER(mg.name_en) LIKE %s")
                        params.append(f"%{muscle.lower()}%")
                    query += f" AND ({' OR '.join(muscle_conditions)})"
                
                # Add muscle_region filter (AI-FILTERABLE)
                if muscle_regions:
                    region_conditions = []
                    for region in muscle_regions:
                        region_conditions.append("LOWER(mr.name_en) LIKE %s")
                        params.append(f"%{region.lower()}%")
                    query += f" AND ({' OR '.join(region_conditions)})"
                
                # Add equipment filter (USER-PROVIDED)
                if equipment:
                    # Special handling for bodyweight
                    if 'bodyweight' in [e.lower() for e in equipment]:
                        equipment_conditions = ["eq.name_en IS NULL"]
                        for equip in equipment:
                            if equip.lower() != 'bodyweight':
                                equipment_conditions.append("LOWER(eq.name_en) LIKE %s")
                                params.append(f"%{equip.lower()}%")
                        query += f" AND ({' OR '.join(equipment_conditions)})"
                    else:
                        equipment_conditions = []
                        for equip in equipment:
                            equipment_conditions.append("LOWER(eq.name_en) LIKE %s")
                            params.append(f"%{equip.lower()}%")
                        query += f" AND ({' OR '.join(equipment_conditions)})"
                
                # Add goals filter (AI-FILTERABLE)
                if goals:
                    goal_conditions = []
                    for goal in goals:
                        goal_conditions.append("LOWER(g.name_en) LIKE %s")
                        params.append(f"%{goal.lower()}%")
                    query += f" AND ({' OR '.join(goal_conditions)})"
                
                # Add mechanics filter (AI-FILTERABLE)
                if mechanics:
                    mechanics_conditions = []
                    for mech in mechanics:
                        mechanics_conditions.append("LOWER(mech.name_en) LIKE %s")
                        params.append(f"%{mech.lower()}%")
                    query += f" AND ({' OR '.join(mechanics_conditions)})"
                
                # Add position filter (AI-FILTERABLE)
                if position:
                    position_conditions = []
                    for pos in position:
                        position_conditions.append("LOWER(pos.name_en) LIKE %s")
                        params.append(f"%{pos.lower()}%")
                    query += f" AND ({' OR '.join(position_conditions)})"
                
                # Add training phase filter (AI-FILTERABLE)
                if training_phase:
                    phase_conditions = []
                    for phase in training_phase:
                        phase_conditions.append("LOWER(tp.name_en) LIKE %s")
                        params.append(f"%{phase.lower()}%")
                    query += f" AND ({' OR '.join(phase_conditions)})"
                
                # Add style filter (AI-FILTERABLE) - style_id is direct FK in exercise table
                if style:
                    style_conditions = []
                    for st in style:
                        style_conditions.append("LOWER(s.name_en) LIKE %s")
                        params.append(f"%{st.lower()}%")
                    query += f" AND ({' OR '.join(style_conditions)})"
                
                # Group by and limit
                query += """
                    GROUP BY e.exercise_id, e.name_en, e.name_fa, e.instructions_en, 
                             e.instructions_fa, d.name_en, s.name_en
                    LIMIT %s
                """
                params.append(limit)
                
                # Execute query
                cursor.execute(query, params)
                
                # Format results
                for row in cursor.fetchall():
                    exercises.append({
                        "exercise_id": row[0],
                        "name": row[1],
                        "name_fa": row[2],
                        "instructions": row[3] if row[3] else [],
                        "instructions_fa": row[4] if row[4] else [],
                        "difficulty": row[5] or "Unknown",
                        "equipment": row[6] or "Bodyweight",
                        "muscle_groups": row[7] or "Full Body",
                        "muscle_regions": row[8] or "General",
                        "goals": row[9] or "General Fitness",
                        "mechanics": row[10] or "Unknown",
                        "position": row[11] or "Unknown",
                        "training_phase": row[12] or "Main Lift",
                        "style": row[13] or "Standard"
                    })
        
        finally:
            conn.close()
        
        return exercises
    
    def search_by_muscle_group(self, muscle_group: str, difficulty: str, 
                               equipment: List[str], limit: int = 30) -> List[Dict]:
        """
        Search exercises targeting specific muscle group.
        
        Args:
            muscle_group: Target muscle group (Glutes, Arms, Back, Quads, etc.)
            difficulty: Difficulty level (Beginner, Novice, Intermediate, Advanced)
            equipment: Available equipment list
            limit: Maximum results
        """
        return self.search_exercises(
            difficulty=difficulty,
            muscle_groups=[muscle_group],
            equipment=equipment,
            limit=limit
        )
    
    def search_warmup_exercises(self, muscle_focus: Optional[str] = None, 
                                equipment: List[str] = None, limit: int = 15) -> List[Dict]:
        """
        Search for warmup exercises.
        
        Args:
            muscle_focus: Optional muscle group to focus warmup on
            equipment: Available equipment
            limit: Maximum results
        """
        return self.search_exercises(
            training_phase=['Warm-up', 'Warmup'],
            muscle_groups=[muscle_focus] if muscle_focus else None,
            equipment=equipment,
            limit=limit
        )
    
    def search_cooldown_exercises(self, muscle_focus: Optional[str] = None,
                                  limit: int = 15) -> List[Dict]:
        """
        Search for cooldown/stretching exercises.
        
        Args:
            muscle_focus: Optional muscle group to focus cooldown on
            limit: Maximum results
        """
        return self.search_exercises(
            training_phase=['Cool-down', 'Cooldown'],
            style=['Stretches', 'Recovery'],
            muscle_groups=[muscle_focus] if muscle_focus else None,
            limit=limit
        )
    
    def search_cardio_exercises(self, difficulty: str, equipment: List[str], 
                                limit: int = 20) -> List[Dict]:
        """
        Search for cardio/conditioning exercises.
        
        Args:
            difficulty: Difficulty level
            equipment: Available equipment
            limit: Maximum results
        """
        return self.search_exercises(
            difficulty=difficulty,
            style=['Cardio'],
            equipment=equipment,
            limit=limit
        )
    
    def search_recovery_exercises(self, limit: int = 15) -> List[Dict]:
        """
        Search for recovery exercises.
        
        Args:
            limit: Maximum results
        """
        return self.search_exercises(
            style=['Recovery'],
            limit=limit
        )


# ─────────────────────────────────────────────
# AVALAI WORKOUT PLAN GENERATOR
# ─────────────────────────────────────────────
class AvalAIWorkoutPlanGenerator:
    """AI-powered workout plan generator using AvalAI Gemini API and SQL-based exercise search"""
    
    def __init__(self, search_engine: SQLExerciseSearchEngine):
        self.search_engine = search_engine
    
    def generate_weekly_plan(self, user_profile: Dict) -> Dict:
        """
        Generate a complete weekly workout plan based on user profile.
        
        Args:
            user_profile: Dictionary containing:
                - user_id: User identifier
                - age: User age
                - weight: User weight (kg)
                - height: User height (cm)
                - gender: User gender
                - goal: Training goal (lose_weight, build_muscle, improve_endurance, etc.)
                - experience: Experience level (beginner, intermediate, advanced, expert)
                - trainingDays: Number of training days per week (1-7)
                - workoutLimitations: Any physical limitations or injuries
                - specializedSport: Sport-specific training requirements
                - trainingLocation: Training location (home, gym, outdoor)
                - homeEquipment: Available equipment list
                
        Returns:
            Complete workout plan with weekly structure
        """
        # Extract user profile details
        age = user_profile.get('age', 30)
        weight = user_profile.get('weight', 70)
        height = user_profile.get('height', 170)
        gender = user_profile.get('gender', 'male')
        goal = user_profile.get('goal', 'general_fitness')
        experience = user_profile.get('experience', 'beginner')
        training_days = user_profile.get('trainingDays', 3)
        limitations = user_profile.get('workoutLimitations', 'No limitations')
        specialized_sport = user_profile.get('specializedSport', 'None')
        location = user_profile.get('trainingLocation', 'home')
        equipment = user_profile.get('homeEquipment', ['bodyweight'])
        
        # Map experience to difficulty
        difficulty_mapping = {
            'beginner': 'Beginner',
            'intermediate': 'Novice',
            'advanced': 'Intermediate',
            'expert': 'Advanced'
        }
        difficulty = difficulty_mapping.get(experience.lower(), 'Beginner')
        
        # Map goals to training strategies
        goal_strategies = {
            'lose_weight': {
                'focus_areas': ['Full Body', 'Core'],
                'muscle_groups': ['Glutes', 'Quads', 'Core', 'Back'],
                'goals': ['Endurance', 'Full Body', 'Core Strength'],
                'mechanics': ['Compound', 'Dynamic'],
                'style': ['Cardio']
            },
            'build_muscle': {
                'focus_areas': ['Chest', 'Back', 'Legs', 'Shoulders', 'Arms'],
                'muscle_groups': ['Chest', 'Back', 'Quads', 'Shoulders', 'Arms'],
                'goals': ['Strength', 'Hypertrophy', 'Muscle Building'],
                'mechanics': ['Compound', 'Isolation']
            },
            'improve_endurance': {
                'focus_areas': ['Full Body', 'Core', 'Legs'],
                'muscle_groups': ['Glutes', 'Quads', 'Core', 'Back'],
                'goals': ['Endurance', 'Muscle Endurance', 'Stamina'],
                'mechanics': ['Dynamic', 'Compound'],
                'style': ['Cardio']
            },
            'general_fitness': {
                'focus_areas': ['Full Body', 'Core'],
                'muscle_groups': ['Glutes', 'Quads', 'Core', 'Back', 'Chest'],
                'goals': ['Full Body', 'Core Strength'],
                'mechanics': ['Compound', 'Dynamic']
            },
            'increase_strength': {
                'focus_areas': ['Compound movements', 'Full Body'],
                'muscle_groups': ['Back', 'Chest', 'Quads', 'Glutes'],
                'goals': ['Strength', 'Power'],
                'mechanics': ['Compound']
            }
        }
        
        strategy = goal_strategies.get(goal, goal_strategies['general_fitness'])
        
        print(f"🎯 Generating workout plan for: {user_profile.get('user_id', 'Unknown User')}")
        print(f"   Goal: {goal} | Experience: {experience} | Training Days: {training_days}")
        print(f"   Difficulty: {difficulty} | Equipment: {', '.join(equipment[:3])}...")
        
        # Generate weekly split
        weekly_split = self._generate_weekly_split(
            training_days, strategy['focus_areas'], specialized_sport
        )
        
        # Search for exercises for each day
        print("\n🔍 Searching exercises from database...")
        weekly_exercises = []
        for day_info in weekly_split:
            print(f"   Day {day_info['day']}: {day_info['focus']}")
            day_exercises = self._search_exercises_for_day(
                day_info, difficulty, equipment, strategy
            )
            weekly_exercises.append({
                'day': day_info['day'],
                'focus': day_info['focus'],
                'muscle_groups': day_info['muscle_groups'],
                'exercises': day_exercises
            })
            print(f"      Found: {len(day_exercises['warmup'])} warmup, "
                  f"{len(day_exercises['main'])} main, {len(day_exercises['cooldown'])} cooldown")
        
        # Generate structured plan using AvalAI
        print("\n🤖 Generating structured plan with AvalAI Gemini API...")
        workout_plan = self._generate_plan_with_avalai(
            user_profile, weekly_exercises, limitations, strategy, difficulty
        )
        
        print("✅ Workout plan generation complete!\n")
        
        return {
            "user_id": user_profile.get('user_id', 'unknown'),
            "plan_type": "weekly",
            "training_days": training_days,
            "difficulty": difficulty,
            "goal": goal,
            "workout_plan": workout_plan,
            "generated_by": "avalai_sql_search_engine"
        }
    
    def _generate_weekly_split(self, training_days: int, focus_areas: List[str],
                               specialized_sport: str) -> List[Dict]:
        """Generate weekly training split with specific muscle targets"""
        
        # Handle specialized sports
        if 'marathon' in specialized_sport.lower() or 'running' in specialized_sport.lower():
            if training_days <= 3:
                return [
                    {'day': 1, 'focus': 'Running + Core', 'muscle_groups': ['Core', 'Quads']},
                    {'day': 2, 'focus': 'Leg Strength', 'muscle_groups': ['Quads', 'Glutes']},
                    {'day': 3, 'focus': 'Recovery + Flexibility', 'muscle_groups': ['Full Body']}
                ][:training_days]
            elif training_days == 4:
                return [
                    {'day': 1, 'focus': 'Running + Core', 'muscle_groups': ['Core', 'Quads']},
                    {'day': 2, 'focus': 'Leg Strength', 'muscle_groups': ['Quads', 'Glutes']},
                    {'day': 3, 'focus': 'Upper Body', 'muscle_groups': ['Chest', 'Back', 'Arms']},
                    {'day': 4, 'focus': 'Recovery + Flexibility', 'muscle_groups': ['Full Body']}
                ]
            else:
                return [
                    {'day': 1, 'focus': 'Running + Cardio', 'muscle_groups': ['Quads', 'Core']},
                    {'day': 2, 'focus': 'Leg Strength', 'muscle_groups': ['Quads', 'Glutes']},
                    {'day': 3, 'focus': 'Core + Stability', 'muscle_groups': ['Core', 'Back']},
                    {'day': 4, 'focus': 'Upper Body', 'muscle_groups': ['Chest', 'Back', 'Shoulders']},
                    {'day': 5, 'focus': 'Running + Intervals', 'muscle_groups': ['Quads', 'Core']},
                    {'day': 6, 'focus': 'Full Body', 'muscle_groups': ['Full Body']},
                    {'day': 7, 'focus': 'Recovery + Flexibility', 'muscle_groups': ['Full Body']}
                ][:training_days]
        
        # Standard training splits
        if training_days <= 3:
            return [
                {'day': 1, 'focus': 'Full Body Strength', 'muscle_groups': ['Chest', 'Back', 'Quads']},
                {'day': 2, 'focus': 'Upper Body', 'muscle_groups': ['Chest', 'Back', 'Shoulders', 'Arms']},
                {'day': 3, 'focus': 'Lower Body + Core', 'muscle_groups': ['Quads', 'Glutes', 'Core']}
            ][:training_days]
        
        elif training_days == 4:
            return [
                {'day': 1, 'focus': 'Upper Push (Chest & Triceps)', 'muscle_groups': ['Chest', 'Arms', 'Shoulders']},
                {'day': 2, 'focus': 'Lower Body (Legs & Glutes)', 'muscle_groups': ['Quads', 'Glutes', 'Calves']},
                {'day': 3, 'focus': 'Upper Pull (Back & Biceps)', 'muscle_groups': ['Back', 'Arms']},
                {'day': 4, 'focus': 'Core + Cardio', 'muscle_groups': ['Core', 'Full Body']}
            ]
        
        elif training_days == 5:
            return [
                {'day': 1, 'focus': 'Chest & Triceps', 'muscle_groups': ['Chest', 'Arms']},
                {'day': 2, 'focus': 'Back & Biceps', 'muscle_groups': ['Back', 'Arms']},
                {'day': 3, 'focus': 'Legs & Glutes', 'muscle_groups': ['Quads', 'Glutes', 'Hamstrings']},
                {'day': 4, 'focus': 'Shoulders & Core', 'muscle_groups': ['Shoulders', 'Core']},
                {'day': 5, 'focus': 'Full Body + Cardio', 'muscle_groups': ['Full Body']}
            ]
        
        else:  # 6+ days
            return [
                {'day': 1, 'focus': 'Chest', 'muscle_groups': ['Chest', 'Arms']},
                {'day': 2, 'focus': 'Back', 'muscle_groups': ['Back', 'Arms']},
                {'day': 3, 'focus': 'Legs', 'muscle_groups': ['Quads', 'Glutes', 'Hamstrings']},
                {'day': 4, 'focus': 'Shoulders', 'muscle_groups': ['Shoulders']},
                {'day': 5, 'focus': 'Arms + Core', 'muscle_groups': ['Arms', 'Core']},
                {'day': 6, 'focus': 'Full Body + Cardio', 'muscle_groups': ['Full Body']},
                {'day': 7, 'focus': 'Recovery + Flexibility', 'muscle_groups': ['Full Body']}
            ][:training_days]
    
    def _search_exercises_for_day(self, day_info: Dict, difficulty: str,
                                  equipment: List[str], strategy: Dict) -> Dict:
        """Search for exercises for a specific training day"""
        
        muscle_groups = day_info['muscle_groups']
        focus = day_info['focus']
        
        # Search warmup exercises
        warmup_muscle = muscle_groups[0] if muscle_groups and muscle_groups[0] != 'Full Body' else None
        warmup_exercises = self.search_engine.search_warmup_exercises(
            muscle_focus=warmup_muscle,
            equipment=equipment,
            limit=15
        )
        
        # Search main exercises by muscle groups
        main_exercises = []
        seen_ids = set()
        
        for muscle in muscle_groups:
            if muscle == 'Full Body':
                # Get compound movements
                exercises = self.search_engine.search_exercises(
                    difficulty=difficulty,
                    mechanics=strategy.get('mechanics', ['Compound']),
                    equipment=equipment,
                    goals=strategy.get('goals', ['Full Body']),
                    limit=30
                )
            else:
                # Get muscle-specific exercises
                exercises = self.search_engine.search_by_muscle_group(
                    muscle_group=muscle,
                    difficulty=difficulty,
                    equipment=equipment,
                    limit=20
                )
            
            # Deduplicate
            for ex in exercises:
                if ex['exercise_id'] not in seen_ids:
                    main_exercises.append(ex)
                    seen_ids.add(ex['exercise_id'])
        
        # Add cardio if needed
        if 'cardio' in focus.lower() or 'hiit' in focus.lower():
            cardio_exercises = self.search_engine.search_cardio_exercises(
                difficulty=difficulty,
                equipment=equipment,
                limit=10
            )
            for ex in cardio_exercises:
                if ex['exercise_id'] not in seen_ids:
                    main_exercises.append(ex)
                    seen_ids.add(ex['exercise_id'])
        
        # Add recovery exercises if needed
        if 'recovery' in focus.lower() or 'flexibility' in focus.lower():
            recovery_exercises = self.search_engine.search_recovery_exercises(limit=15)
            for ex in recovery_exercises:
                if ex['exercise_id'] not in seen_ids:
                    main_exercises.append(ex)
                    seen_ids.add(ex['exercise_id'])
        
        # Search cooldown exercises
        cooldown_muscle = muscle_groups[0] if muscle_groups and muscle_groups[0] != 'Full Body' else None
        cooldown_exercises = self.search_engine.search_cooldown_exercises(
            muscle_focus=cooldown_muscle,
            limit=15
        )
        
        # If not enough cooldown exercises, get generic stretches
        # If not enough cooldown exercises, get generic stretches
        if len(cooldown_exercises) < 5:
            generic_cooldown = self.search_engine.search_exercises(
                style=['Stretches', 'Recovery'],
                limit=15
            )
            cooldown_exercises.extend(generic_cooldown)
        return {
            'warmup': warmup_exercises[:15],
            'main': main_exercises[:50],
            'cooldown': cooldown_exercises[:15]
        }
    
    def _generate_plan_with_avalai(self, user_profile: Dict, weekly_exercises: List[Dict],
                                   limitations: str, strategy: Dict, difficulty: str) -> List[Dict]:
        """Use AvalAI Gemini API to structure the workout plan"""
        
        # Prepare the prompt
        system_instructions = """You are MovoKio, an expert personal trainer and exercise scientist with deep knowledge in sports science, biomechanics, and periodization.

Create a highly personalized weekly workout plan using the exercise database provided. Each exercise has been pre-filtered based on the user's profile.

RESPONSE FORMAT - CRITICAL:
Return ONLY a valid JSON array. No markdown, no code blocks, no explanations.

Each day object must contain:
- day (number): training day index (1, 2, 3, ...)
- focus (string): main training goal for that day
- warmup (array): 2-4 dynamic warmup exercises with fields: id, name, sets, reps
- exercises (array): 4-8 main exercises with fields: id, name, sets, reps, rest_seconds
- cooldown (array): 2-4 cooldown exercises with fields: id, name, duration_minutes
- note (string): personalized coaching tip for that day (2-3 sentences)

EXERCISE SELECTION GUIDELINES:
1. **Volume by Experience Level**:
   - Beginner: 3 sets, 10-12 reps, 4-5 main exercises
   - Novice: 3-4 sets, 8-12 reps, 5-6 main exercises
   - Intermediate: 4 sets, 6-12 reps, 6-7 main exercises
   - Advanced: 4-5 sets, 6-10 reps, 7-8 main exercises

2. **Exercise Order**: Start with compound movements, then isolation

3. **Variety**: Choose exercises targeting muscles from different angles

4. **Progression**: Include variations in rep ranges for different goals:
   - Strength: 4-6 reps, 2-3 min rest
   - Hypertrophy: 8-12 reps, 60-90 sec rest
   - Endurance: 12-15+ reps, 30-60 sec rest

5. **Safety**: Respect user limitations and provide modifications in notes

6. **Warm-up/Cool-down**: Essential for injury prevention and recovery

PERSONALIZATION:
- Adjust volume based on age and recovery capacity
- Consider specialized sport requirements
- Balance muscle groups for symmetry
- Include unilateral exercises when appropriate
- Provide form cues and safety reminders in notes

OUTPUT: Pure JSON array only, starting with [ and ending with ]"""

        user_message = f"""User Profile:
- Age: {user_profile.get('age')} years
- Weight: {user_profile.get('weight')} kg
- Height: {user_profile.get('height')} cm
- Gender: {user_profile.get('gender')}
- Goal: {user_profile.get('goal')}
- Experience: {user_profile.get('experience')} (Difficulty: {difficulty})
- Training Days: {user_profile.get('trainingDays')} days/week
- Limitations: {limitations}
- Specialized Sport: {user_profile.get('specializedSport', 'None')}
- Location: {user_profile.get('trainingLocation')}
- Equipment: {', '.join(user_profile.get('homeEquipment', ['bodyweight']))}

Training Strategy:
- Focus Areas: {', '.join(strategy['focus_areas'])}
- Target Muscle Groups: {', '.join(strategy['muscle_groups'])}
- Training Goals: {', '.join(strategy['goals'])}
- Preferred Mechanics: {', '.join(strategy['mechanics'])}

Available Exercises by Day:
"""

        for day_ex in weekly_exercises:
            user_message += f"\n=== DAY {day_ex['day']}: {day_ex['focus']} ===\n"
            user_message += f"Target Muscles: {', '.join(day_ex['muscle_groups'])}\n\n"
            
            user_message += "WARMUP OPTIONS:\n"
            for ex in day_ex['exercises']['warmup'][:10]:
                user_message += f"  - ID {ex['exercise_id']}: {ex['name']} ({ex['equipment']})\n"
            
            user_message += "\nMAIN EXERCISE OPTIONS:\n"
            for ex in day_ex['exercises']['main'][:30]:
                user_message += f"  - ID {ex['exercise_id']}: {ex['name']}\n"
                user_message += f"    Equipment: {ex['equipment']}, Mechanics: {ex['mechanics']}\n"
                user_message += f"    Muscles: {ex['muscle_groups']}\n"
            
            user_message += "\nCOOLDOWN OPTIONS:\n"
            for ex in day_ex['exercises']['cooldown'][:10]:
                user_message += f"  - ID {ex['exercise_id']}: {ex['name']} ({ex['equipment']})\n"
            
            user_message += "\n"

        user_message += """
Now create a complete weekly workout plan following the format specified. Select the most appropriate exercises for each day based on the user's profile and goals. Return ONLY valid JSON."""

        # Call AvalAI API
        try:
            response_text = self._call_avalai_api(system_instructions, user_message)
            
            # Parse JSON response
            workout_plan = self._parse_json_response(response_text)
            
            return workout_plan
            
        except Exception as e:
            print(f"❌ Error generating plan with AvalAI: {e}")
            print("⚠️  Falling back to basic plan structure...")
            return self._generate_fallback_plan(weekly_exercises)
    
    def _call_avalai_api(self, system_instructions: str, user_message: str, 
                         max_retries: int = 3) -> str:
        """Call AvalAI API with retry logic"""
        
        # Prepare request payload
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"{system_instructions}\n\n{user_message}"
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topP": 0.9,
                "topK": 40,
                "maxOutputTokens": 8192
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": AVALAI_API_KEY
        }
        
        api_url = f"{AVALAI_BASE_URL}/v1beta/models/{GEMINI_MODEL}:generateContent"
        
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                print(f"   Calling AvalAI API (attempt {attempt + 1}/{max_retries})...")
                
                response = requests.post(
                    api_url,
                    headers=headers,
                    json=payload,
                    timeout=120
                )
                
                response.raise_for_status()
                print(f"   ✓ API call successful")
                break
                
            except requests.exceptions.HTTPError as e:
                if response.status_code == 400:
                    print(f"   ✗ API returned 400 error: {response.text[:500]}")
                    raise ValueError(f"API 400 Error: {response.text[:500]}")
                
                if attempt < max_retries - 1:
                    print(f"   ⚠️  API error (attempt {attempt + 1}/{max_retries}), retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    print(f"   ✗ All retry attempts failed")
                    raise
                    
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    print(f"   ⚠️  Request timeout (attempt {attempt + 1}/{max_retries}), retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    print(f"   ✗ All retry attempts failed due to timeout")
                    raise
        
        # Parse response JSON
        try:
            response_json = response.json()
            response_text = response_json["candidates"][0]["content"]["parts"][0]["text"].strip()
            return response_text
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            print(f"   ✗ Failed to parse API response: {e}")
            raise
    
    def _parse_json_response(self, response_text: str) -> List[Dict]:
        """Parse JSON response from API, handling markdown and formatting issues"""
        
        # Remove markdown code blocks if present
        if "```json" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            response_text = response_text[start:end].strip()
        elif "```" in response_text:
            start = response_text.find("```") + 3
            end = response_text.find("```", start)
            response_text = response_text[start:end].strip()
        
        # Try to find JSON array if it's embedded in text
        if not response_text.startswith("["):
            start_idx = response_text.find("[")
            end_idx = response_text.rfind("]") + 1
            if start_idx != -1 and end_idx > start_idx:
                response_text = response_text[start_idx:end_idx]
        
        # Try to parse JSON
        try:
            workout_plan = json.loads(response_text)
            print(f"   ✓ Successfully parsed workout plan with {len(workout_plan)} days")
            return workout_plan
        except json.JSONDecodeError as e:
            print(f"   ✗ JSON parsing error: {e}")
            print(f"   Response preview: {response_text[:500]}")
            raise
    
    def _generate_fallback_plan(self, weekly_exercises: List[Dict]) -> List[Dict]:
        """Generate a basic fallback plan if AI generation fails"""
        
        fallback_plan = []
        
        for day_ex in weekly_exercises:
            day_plan = {
                "day": day_ex['day'],
                "focus": day_ex['focus'],
                "warmup": [],
                "exercises": [],
                "cooldown": [],
                "note": f"Focus on {day_ex['focus']} with proper form and controlled movements."
            }
            
            # Add warmup
            for ex in day_ex['exercises']['warmup'][:3]:
                day_plan['warmup'].append({
                    "id": ex['exercise_id'],
                    "name": ex['name'],
                    "sets": 1,
                    "reps": 10
                })
            
            # Add main exercises
            for ex in day_ex['exercises']['main'][:6]:
                day_plan['exercises'].append({
                    "id": ex['exercise_id'],
                    "name": ex['name'],
                    "sets": 3,
                    "reps": 10,
                    "rest_seconds": 60
                })
            
            # Add cooldown
            for ex in day_ex['exercises']['cooldown'][:3]:
                day_plan['cooldown'].append({
                    "id": ex['exercise_id'],
                    "name": ex['name'],
                    "duration_minutes": 2
                })
            
            fallback_plan.append(day_plan)
        
        return fallback_plan


# ─────────────────────────────────────────────
# MAIN API FUNCTION
# ─────────────────────────────────────────────
def generate_workout_plan(user_profile: Dict) -> Dict:
    """
    Main function to generate a workout plan using AvalAI API and SQL-based search.
    
    Args:
        user_profile: User profile dictionary containing:
            - user_id, age, weight, height, gender
            - goal, experience, trainingDays
            - workoutLimitations, specializedSport
            - trainingLocation, homeEquipment
            
    Returns:
        Complete workout plan dictionary
    """
    # Initialize components
    search_engine = SQLExerciseSearchEngine(DB_CONFIG)
    plan_generator = AvalAIWorkoutPlanGenerator(search_engine)
    
    # Generate the plan
    result = plan_generator.generate_weekly_plan(user_profile)
    
    return result


# ─────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────
if __name__ == "__main__":
    # Example user profile
    test_profile = {
        "user_id": "test_user_avalai_001",
        "age": 28,
        "weight": 75,
        "height": 175,
        "gender": "male",
        "goal": "build_muscle",
        "experience": "intermediate",
        "trainingDays": 4,
        "dietaryRestrictions": "None",
        "workoutLimitations": "No limitations",
        "specializedSport": "None",
        "trainingLocation": "gym",
        "homeEquipment": ["Dumbbells", "Barbell", "Bodyweight", "Pull-up Bar"]
    }
    
    print("=" * 80)
    print("🏋️  MOVOKIO AVALAI WORKOUT PLAN GENERATOR")
    print("=" * 80)
    print(f"\n📋 User Profile:")
    print(f"   ID: {test_profile['user_id']}")
    print(f"   Goal: {test_profile['goal']}")
    print(f"   Experience: {test_profile['experience']}")
    print(f"   Training Days: {test_profile['trainingDays']}")
    print(f"   Equipment: {', '.join(test_profile['homeEquipment'])}")
    print("\n" + "-" * 80 + "\n")
    
    # Generate plan
    result = generate_workout_plan(test_profile)
    
    # Save to file
    output_file = "avalai_workout_plan_output.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 80)
    print("📊 PLAN SUMMARY")
    print("=" * 80)
    
    for day in result['workout_plan']:
        print(f"\nDay {day['day']}: {day['focus']}")
        print(f"  Warmup: {len(day.get('warmup', []))} exercises")
        print(f"  Main: {len(day.get('exercises', []))} exercises")
        print(f"  Cooldown: {len(day.get('cooldown', []))} exercises")
        if 'note' in day:
            print(f"  Note: {day['note'][:80]}...")
    
    print(f"\n✅ Complete plan saved to: {output_file}")
    print("=" * 80)
