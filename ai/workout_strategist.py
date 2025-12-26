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
GEMINI_MODEL = "gemini-2.5-pro"


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
                - workout_goal_id: Training goal ID
                - physical_fitness: Fitness level (beginner/intermediate/advanced/expert)
                - fitness_days: Number of training days per week (3-6)
                - workout_limitations: Physical limitations or injuries
                - specialized_sport: Sport-specific training requirements
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
        training_days = user_profile.get('fitness_days', 3)
        limitations = user_profile.get('workout_limitations', 'بدون محدودیت')
        specialized_sport = user_profile.get('specialized_sport', 'ندارد')
        location = user_profile.get('training_location', 'home')
        
        # Map workout goal ID to Persian goal name
        goal_mapping = {
            1: 'کاهش وزن و چربی‌سوزی',
            2: 'افزایش حجم عضلانی',
            3: 'افزایش قدرت',
            4: 'بهبود استقامت قلبی-عروقی',
            5: 'تناسب اندام عمومی',
            6: 'افزایش انعطاف‌پذیری'
        }
        goal_id = user_profile.get('workout_goal_id', 5)
        goal = goal_mapping.get(goal_id, 'تناسب اندام عمومی')
        
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
2. طراحی استراتژی ۱۲ هفته‌ای با فازبندی منطقی
3. در نظر گرفتن پیشرفت تدریجی (Progressive Overload)
4. توجه به دوره‌های ریکاوری و Deload
5. تطبیق برنامه با تجهیزات موجود و محدودیت‌های کاربر

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
- هیچ علامت markdown استفاده نکنید (بدون *, **, ___, ##)
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
- تعداد روزهای تمرین در هفته: {training_days} روز
- محدودیت‌های ورزشی: {limitations}
- ورزش تخصصی: {specialized_sport}
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
        goal_id = user_profile.get('workout_goal_id', 5)
        fitness_level = user_profile.get('physical_fitness', 'beginner')
        
        # Goal-specific strategies
        goal_strategies = {
            1: "کاهش وزن و چربی‌سوزی",
            2: "افزایش حجم عضلانی",
            3: "افزایش قدرت",
            4: "بهبود استقامت",
            5: "تناسب اندام عمومی"
        }
        goal_name = goal_strategies.get(goal_id, "تناسب اندام عمومی")
        
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
            - workout_goal_id, physical_fitness, fitness_days
            - workout_limitations, specialized_sport
            - training_location, equipment_ids
            
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
        "workout_goal_id": 2,  # Build muscle
        "physical_fitness": "intermediate",
        "fitness_days": 4,
        "workout_limitations": "بدون محدودیت",
        "specialized_sport": "ندارد",
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
