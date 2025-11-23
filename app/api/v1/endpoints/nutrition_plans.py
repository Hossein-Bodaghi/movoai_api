"""
Nutrition Plan endpoints (Phase 3)
Includes mock AI generation for nutrition plans until AI agents are implemented
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
import random

from app.database.session import get_db
from app.models.user import User
from app.models.nutrition_plan import NutritionPlan, NutritionWeek, NutritionDay, Meal
from app.models.nutrition_goal import NutritionGoal
from app.schemas.nutrition_plan import (
    NutritionPlanCreate,
    NutritionPlanResponse,
    NutritionPlanDetailResponse,
    NutritionPlanUpdate,
    NutritionPlanListResponse,
    NutritionWeekCompletionRequest,
    NutritionWeekCompletionResponse,
    NutritionWeekResponse
)
from app.schemas.auth import MessageResponse
from app.dependencies import get_current_user

router = APIRouter()


# ========== Mock AI Generation Functions ==========

def generate_mock_nutrition_strategy(user: User, nutrition_goal: NutritionGoal, total_weeks: int) -> str:
    """Generate mock AI strategy for nutrition plan"""
    return "این برنامه غذایی بر اساس نیازهای کالری و اهداف شما طراحی شده است. استراتژی این برنامه تنظیم ماکروها به صورت متعادل و استفاده از منابع غذایی تمیز است. وعده‌های غذایی به گونه‌ای تنظیم شده‌اند که انرژی شما در طول روز ثابت بماند. برنامه شامل میان‌وعده‌های سالم برای جلوگیری از گرسنگی است."


def generate_mock_nutrition_expectations(total_weeks: int) -> str:
    """Generate mock AI expectations for nutrition plan"""
    return "با پیروی از این برنامه غذایی، انتظار می‌رود در ۱۲ هفته بین ۶ تا ۱۰ کیلوگرم کاهش وزن داشته باشید (بسته به وزن اولیه). افزایش انرژی و بهبود کیفیت خواب از هفته اول محسوس خواهد بود. تغییرات ترکیب بدنی از هفته ۴ به بعد قابل مشاهده است. در پایان برنامه، عادات غذایی سالم‌تری خواهید داشت."


def generate_mock_meals(meal_type: str, day_number: int, base_calories: int) -> dict:
    """Generate mock meal data in Persian format"""
    # Persian meals based on user's example
    meals_database = {
        "breakfast": [
            {"name": "املت گوجه و قارچ", "desc": "سه عدد تخم‌مرغ را با گوجه فرنگی خرد شده و قارچ تفت داده شده مخلوط کرده و در تابه بپزید. همراه با یک کف دست نان سنگک میل شود.", "cal": 450},
            {"name": "جو دوسر پرک با شیر و موز", "desc": "نصف لیوان جو دوسر پرک را با یک لیوان شیر روی حرارت ملایم بپزید. در انتها یک عدد موز خرد شده و کمی دارچین اضافه کنید.", "cal": 480},
            {"name": "نان و پنیر و گردو", "desc": "دو کف دست نان سنگک همراه با ۴۰ گرم پنیر کم‌چرب، دو عدد گردو و خیار و گوجه.", "cal": 400},
            {"name": "اسموتی پروتئینی", "desc": "یک لیوان شیر، یک عدد موز، یک قاشق کره بادام‌زمینی و نصف پیمانه جو دوسر پرک را در مخلوط‌کن ترکیب کنید.", "cal": 550},
            {"name": "تخم‌مرغ آب‌پز و آووکادو", "desc": "دو عدد تخم‌مرغ آب‌پز همراه با نصف یک آووکادوی کوچک و یک تکه نان تست جو.", "cal": 450},
            {"name": "فرنی جو دوسر", "desc": "نصف لیوان جو دوسر پرک را با یک لیوان شیر و یک قاشق عسل بپزید و با پودر دارچین میل کنید.", "cal": 480},
            {"name": "نیمرو با نان تست", "desc": "دو عدد تخم‌مرغ را به صورت نیمرو درآورده و با دو تکه نان تست جو میل کنید.", "cal": 420}
        ],
        "lunch": [
            {"name": "سینه مرغ گریل شده با برنج و سالاد", "desc": "۱۵۰ گرم سینه مرغ مزه‌دار شده را در تابه گریل یا سرخ کنید. همراه با یک لیوان برنج کته (پخته شده در پلوپز) و سالاد فصل سرو کنید.", "cal": 700},
            {"name": "ماهی قزل‌آلا با سبزیجات", "desc": "یک فیله ماهی قزل‌آلا (حدود ۱۸۰ گرم) را با نمک، فلفل و آبلیمو مزه‌دار کرده و در تابه با کمی روغن بپزید. همراه با سبزیجات بخارپز (مثل کلم بروکلی و هویج) سرو کنید.", "cal": 700},
            {"name": "کباب تابه‌ای با گوجه", "desc": "۱۵۰ گرم گوشت چرخ‌کرده کم‌چرب را با پیاز رنده شده مخلوط و در تابه سرخ کنید. همراه با گوجه کبابی و نصف لیوان برنج سرو شود.", "cal": 750},
            {"name": "خوراک مرغ و سبزیجات", "desc": "۱۵۰ گرم سینه مرغ نگینی را با فلفل دلمه‌ای، قارچ و پیاز در تابه تفت دهید. همراه با یک کف دست نان میل کنید.", "cal": 700},
            {"name": "استامبولی پلو با گوشت", "desc": "یک و نیم لیوان استامبولی پلو که با گوشت چرخ‌کرده کم‌چرب در پلوپز آماده شده، همراه با سالاد شیرازی.", "cal": 750},
            {"name": "جوجه کباب تابه‌ای", "desc": "۱۸۰ گرم فیله مرغ خرد شده و زعفرانی را در تابه سرخ کنید. همراه با یک لیوان برنج و گوجه کبابی سرو شود.", "cal": 750}
        ],
        "dinner": [
            {"name": "عدسی", "desc": "یک کاسه بزرگ عدسی که از قبل با پیاز داغ و ادویه پخته شده است. همراه با آبلیمو تازه و یک کف دست نان میل شود.", "cal": 600},
            {"name": "سالاد مرغ و کاهو", "desc": "کاهو، خیار، گوجه و ۱۰۰ گرم مرغ پخته و خرد شده را با سس ماست و آبلیمو مخلوط کنید. همراه با یک تکه نان تست جو میل شود.", "cal": 600},
            {"name": "سوپ جو و مرغ", "desc": "یک کاسه بزرگ سوپ جو که با تکه‌های سینه مرغ، هویج و جعفری پخته شده است. تهیه آن با جوی پرک بسیار سریع است.", "cal": 650},
            {"name": "سالاد لوبیا و نخود", "desc": "مخلوطی از کاهو، یک لیوان حبوبات پخته (لوبیا و نخود)، ذرت، خیار و گوجه با سس روغن زیتون و آبلیمو.", "cal": 650},
            {"name": "میرزاقاسمی", "desc": "ترکیبی از بادمجان کبابی، سیر، گوجه و دو عدد تخم‌مرغ. همراه با یک کف دست نان سنگک سرو شود.", "cal": 600},
            {"name": "خوراک قارچ و اسفناج", "desc": "اسفناج و قارچ را با پیاز تفت داده و در انتها دو عدد تخم‌مرغ روی آن بشکنید. همراه با نان میل شود.", "cal": 550},
            {"name": "کوکو سبزی", "desc": "دو برش متوسط کوکو سبزی که در تابه با روغن کم آماده شده است، همراه با نان و یک کاسه ماست و خیار.", "cal": 650}
        ],
        "snacks": [
            {"name": "ماست یونانی و گردو", "desc": "یک کاسه ماست یونانی کم‌چرب همراه با دو عدد گردوی خرد شده و یک قاشق چای‌خوری عسل.", "cal": 300},
            {"name": "سیب و کره بادام زمینی", "desc": "یک عدد سیب متوسط را برش زده و با یک قاشق غذاخوری کره بادام زمینی میل کنید.", "cal": 250},
            {"name": "میوه فصل", "desc": "یک عدد پرتقال یا دو عدد نارنگی.", "cal": 150},
            {"name": "تخم‌مرغ آب‌پز", "desc": "دو عدد تخم‌مرغ کامل آب‌پز به عنوان میان‌وعده سرشار از پروتئین.", "cal": 160},
            {"name": "یک مشت آجیل مخلوط", "desc": "حدود ۳۰ گرم مخلوط بادام، پسته و فندق خام و بدون نمک.", "cal": 250},
            {"name": "شیک شیر و خرما", "desc": "یک لیوان شیر کم‌چرب را با سه عدد خرما و یک قاشق پودر کاکائو در مخلوط‌کن ترکیب کنید.", "cal": 300},
            {"name": "دوغ و کشمش", "desc": "یک لیوان دوغ کم‌نمک و کم‌چرب همراه با یک مشت کوچک کشمش.", "cal": 200}
        ]
    }
    
    meal = random.choice(meals_database[meal_type])
    
    return {
        "name": meal["name"],
        "description": meal["desc"],
        "calories": meal["cal"],
        "protein": None,  # Not included in user's format
        "carbs": None,
        "fats": None
    }


def generate_mock_nutrition_week(
    db: Session, 
    plan: NutritionPlan, 
    week_number: int,
    user: User
) -> NutritionWeek:
    """Generate a mock nutrition week with meals using Persian data"""
    
    # Persian week data
    nutrition_week_data = [
        {"week": 1, "title": "شروع سفر تغذیه سالم", "description": "هفته اول درباره عادت کردن به برنامه جدید است. **تمرکز غذایی:** آشنایی با اندازه پورشن‌ها و تنظیم کالری روزانه. **نکات کلیدی:** نوشیدن ۸-۱۰ لیوان آب و حذف تدریجی غذاهای فرآوری شده."},
        {"week": 2, "title": "تنظیم ماکروها و میکروها", "description": "بهینه‌سازی نسبت پروتئین، کربوهیدرات و چربی. **تمرکز غذایی:** افزایش پروتئین به ۱.۸-۲.۲ گرم به ازای هر کیلوگرم وزن بدن. **نکات کلیدی:** اضافه کردن سبزیجات رنگارنگ به هر وعده."},
        {"week": 3, "title": "کنترل اشتها و مدیریت گرسنگی", "description": "یادگیری تشخیص گرسنگی واقعی از گرسنگی احساسی. **تمرکز غذایی:** افزودن فیبر و پروتئین برای احساس سیری طولانی‌تر. **نکات کلیدی:** خوردن آهسته و لذت بردن از غذا."},
        {"week": 4, "title": "بهینه‌سازی تایمینگ وعده‌ها", "description": "زمان‌بندی مناسب وعده‌ها برای انرژی بهتر. **تمرکز غذایی:** توزیع کالری در ۴-۵ وعده کوچک در طول روز. **نکات کلیدی:** وعده قبل و بعد از تمرین."},
        {"week": 5, "title": "معرفی غذاهای جدید و متنوع", "description": "افزودن تنوع برای جلوگیری از خستگی برنامه. **تمرکز غذایی:** امتحان کردن منابع پروتئین و کربوهیدرات جدید. **نکات کلیدی:** آشنایی با سوپرفودها."},
        {"week": 6, "title": "مدیریت میل به شیرینی", "description": "استراتژی‌های سالم برای کنترل میل به شیرینی. **تمرکز غذایی:** جایگزین‌های طبیعی و سالم برای دسرها. **نکات کلیدی:** استفاده از میوه‌ها و شیرین‌کننده‌های طبیعی."},
        {"week": 7, "title": "تقویت سیستم ایمنی با تغذیه", "description": "انتخاب غذاهای تقویت‌کننده ایمنی. **تمرکز غذایی:** افزایش ویتامین C، D و روی. **نکات کلیدی:** مصرف پروبیوتیک‌ها برای سلامت روده."},
        {"week": 8, "title": "برنامه‌ریزی وعده‌ها و Meal Prep", "description": "یادگیری آماده‌سازی وعده‌های هفتگی. **تمرکز غذایی:** پخت و نگهداری صحیح غذاها. **نکات کلیدی:** استفاده از ظروف مناسب و فریز کردن."},
        {"week": 9, "title": "مدیریت تغذیه در مناسبت‌ها", "description": "حفظ برنامه در شرایط اجتماعی. **تمرکز غذایی:** استراتژی‌های هوشمندانه برای غذای بیرون. **نکات کلیدی:** تعادل بین لذت و سلامت."},
        {"week": 10, "title": "هیدراتاسیون و نوشیدنی‌های سالم", "description": "اهمیت آب و مایعات مناسب. **تمرکز غذایی:** حذف نوشابه‌ها و نوشیدنی‌های قندی. **نکات کلیدی:** افزودن چای سبز و نوشیدنی‌های طبیعی."},
        {"week": 11, "title": "بهینه‌سازی خواب با تغذیه", "description": "غذاهایی که به خواب بهتر کمک می‌کنند. **تمرکز غذایی:** منیزیم، تریپتوفان و کربوهیدرات‌های پیچیده. **نکات کلیدی:** زمان‌بندی شام و اجتناب از کافئین."},
        {"week": 12, "title": "ایجاد سبک زندگی تغذیه‌ای پایدار", "description": "تبدیل عادات موقت به سبک زندگی. **تمرکز غذایی:** قانون ۸۰/۲۰ برای انعطاف‌پذیری. **نکات کلیدی:** برنامه‌ریزی برای حفظ نتایج در بلندمدت."}
    ]
    
    week_data = nutrition_week_data[week_number - 1] if week_number <= len(nutrition_week_data) else nutrition_week_data[0]
    
    week = NutritionWeek(
        plan_id=plan.plan_id,
        week_number=week_number,
        title=week_data["title"],
        description=week_data["description"]
    )
    db.add(week)
    db.flush()  # Get week_id
    
    # Calculate daily calorie target - convert Decimal to int
    weight = int(user.weight) if user.weight else 70
    age = int(user.age) if user.age else 30
    base_calories = 2000 + weight * 10 - age * 5
    
    # Generate 7 days with Persian names
    day_names = ["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه"]
    
    for day_name in day_names:
        day = NutritionDay(
            week_id=week.week_id,
            day_name=day_name,
            daily_calories=base_calories
        )
        db.add(day)
        db.flush()  # Get day_id
        
        # Add 4 meals per day (breakfast, lunch, dinner, snacks)
        for meal_type in ["breakfast", "lunch", "dinner", "snacks"]:
            meal_data = generate_mock_meals(
                meal_type, 
                day_names.index(day_name) + 1,
                base_calories
            )
            
            meal = Meal(
                day_id=day.day_id,
                meal_type=meal_type,
                name=meal_data["name"],
                description=meal_data["description"],
                calories=meal_data["calories"],
                protein=meal_data["protein"],
                carbs=meal_data["carbs"],
                fats=meal_data["fats"]
            )
            db.add(meal)
    
    return week


# ========== API Endpoints ==========

@router.post("", response_model=NutritionPlanDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_nutrition_plan(
    plan_data: NutritionPlanCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new nutrition plan with AI-generated content.
    Currently uses mock AI generation - will be replaced with real AI agents.
    """
    
    # Validate total_weeks
    if plan_data.total_weeks not in [1, 4, 12]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="total_weeks must be 1, 4, or 12"
        )
    
    # Get nutrition goal if provided
    nutrition_goal = None
    if plan_data.nutrition_goal_id:
        nutrition_goal = db.query(NutritionGoal).filter(
            NutritionGoal.nutrition_goal_id == plan_data.nutrition_goal_id
        ).first()
        if not nutrition_goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nutrition goal not found"
            )
    
    # Generate mock AI content
    strategy = generate_mock_nutrition_strategy(current_user, nutrition_goal, plan_data.total_weeks)
    expectations = generate_mock_nutrition_expectations(plan_data.total_weeks)
    
    # Create nutrition plan
    nutrition_plan = NutritionPlan(
        user_id=current_user.user_id,
        nutrition_goal_id=plan_data.nutrition_goal_id,
        name=plan_data.name,
        total_weeks=plan_data.total_weeks,
        current_week=1,
        completed_weeks=[],
        strategy=strategy,
        expectations=expectations
    )
    db.add(nutrition_plan)
    db.flush()  # Get plan_id
    
    # Generate nutrition weeks with mock AI
    for week_num in range(1, plan_data.total_weeks + 1):
        generate_mock_nutrition_week(db, nutrition_plan, week_num, current_user)
    
    db.commit()
    
    # Reload with all relationships
    plan = db.query(NutritionPlan).options(
        joinedload(NutritionPlan.weeks).joinedload(NutritionWeek.days).joinedload(NutritionDay.meals)
    ).filter(NutritionPlan.plan_id == nutrition_plan.plan_id).first()
    
    return NutritionPlanDetailResponse.model_validate(plan)


@router.get("", response_model=NutritionPlanListResponse)
async def get_user_nutrition_plans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all nutrition plans for the current user
    """
    plans = db.query(NutritionPlan).filter(
        NutritionPlan.user_id == current_user.user_id
    ).order_by(NutritionPlan.created_at.desc()).all()
    
    return NutritionPlanListResponse(
        plans=[NutritionPlanResponse.model_validate(p) for p in plans],
        total=len(plans)
    )


@router.get("/{plan_id}", response_model=NutritionPlanDetailResponse)
async def get_nutrition_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific nutrition plan with all details
    """
    plan = db.query(NutritionPlan).options(
        joinedload(NutritionPlan.weeks).joinedload(NutritionWeek.days).joinedload(NutritionDay.meals)
    ).filter(
        NutritionPlan.plan_id == plan_id,
        NutritionPlan.user_id == current_user.user_id
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nutrition plan not found"
        )
    
    return NutritionPlanDetailResponse.model_validate(plan)


@router.get("/{plan_id}/week/{week_number}", response_model=NutritionWeekResponse)
async def get_nutrition_week(
    plan_id: int,
    week_number: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific week from a nutrition plan
    """
    # Verify plan ownership
    plan = db.query(NutritionPlan).filter(
        NutritionPlan.plan_id == plan_id,
        NutritionPlan.user_id == current_user.user_id
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nutrition plan not found"
        )
    
    # Get the week
    week = db.query(NutritionWeek).options(
        joinedload(NutritionWeek.days).joinedload(NutritionDay.meals)
    ).filter(
        NutritionWeek.plan_id == plan_id,
        NutritionWeek.week_number == week_number
    ).first()
    
    if not week:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Week not found"
        )
    
    return NutritionWeekResponse.model_validate(week)


@router.put("/{plan_id}", response_model=NutritionPlanResponse)
async def update_nutrition_plan(
    plan_id: int,
    plan_update: NutritionPlanUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a nutrition plan (name, current_week)
    """
    plan = db.query(NutritionPlan).filter(
        NutritionPlan.plan_id == plan_id,
        NutritionPlan.user_id == current_user.user_id
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nutrition plan not found"
        )
    
    # Update only provided fields
    update_data = plan_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(plan, field, value)
    
    db.commit()
    db.refresh(plan)
    
    return NutritionPlanResponse.model_validate(plan)


@router.post("/{plan_id}/complete-week", response_model=NutritionWeekCompletionResponse)
async def complete_nutrition_week(
    plan_id: int,
    completion: NutritionWeekCompletionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark a week as completed and advance to the next week
    """
    plan = db.query(NutritionPlan).filter(
        NutritionPlan.plan_id == plan_id,
        NutritionPlan.user_id == current_user.user_id
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nutrition plan not found"
        )
    
    # Validate week number
    if completion.week_number < 1 or completion.week_number > plan.total_weeks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid week number. Must be between 1 and {plan.total_weeks}"
        )
    
    # Add to completed weeks if not already completed
    if completion.week_number not in plan.completed_weeks:
        plan.completed_weeks = plan.completed_weeks + [completion.week_number]
    
    # Advance current_week if completing the current week
    if completion.week_number == plan.current_week and plan.current_week < plan.total_weeks:
        plan.current_week += 1
    
    db.commit()
    db.refresh(plan)
    
    return NutritionWeekCompletionResponse(
        plan_id=plan.plan_id,
        week_number=completion.week_number,
        current_week=plan.current_week,
        completed_weeks=plan.completed_weeks,
        message=f"Week {completion.week_number} marked as completed"
    )


@router.delete("/{plan_id}", response_model=MessageResponse)
async def delete_nutrition_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a nutrition plan (cascades to all weeks, days, and meals)
    """
    plan = db.query(NutritionPlan).filter(
        NutritionPlan.plan_id == plan_id,
        NutritionPlan.user_id == current_user.user_id
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nutrition plan not found"
        )
    
    db.delete(plan)
    db.commit()
    
    return MessageResponse(message="Nutrition plan deleted successfully")
