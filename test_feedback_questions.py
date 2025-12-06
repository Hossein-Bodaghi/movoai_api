"""
Test script for fetching feedback questions from the API
"""
import requests
import json
from pprint import pprint


def test_feedback_questions():
    """Test fetching feedback questions for a specific week"""
    
    # API endpoint
    url = "https://movokio.com/api/v1/feedback/questions"
    
    # Auth token
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxOCwiZXhwIjoxNzY1MDIxMTQzLCJ0eXBlIjoiYWNjZXNzIn0.P9te4f2-YwlSxuYjgFeY_J3XdrzZKfy9w4Ar7cCOrM4"
    }
    
    # Query parameters
    params = {
        "week_table": "workout_weeks",
        "week_number": 1,
        "focus": "efficiency"
    }
    
    print("=" * 80)
    print("Testing Feedback Questions API")
    print("=" * 80)
    print(f"\nURL: {url}")
    print(f"Parameters: {json.dumps(params, indent=2)}")
    print("\n" + "-" * 80)
    
    try:
        # Make GET request
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        # Print response status
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Time: {response.elapsed.total_seconds():.2f}s")
        
        # Check if request was successful
        if response.status_code == 200:
            data = response.json()
            print("\n✓ Success! Response:")
            print("-" * 80)
            pprint(data, width=120)
            
            # Display summary
            print("\n" + "=" * 80)
            print("Summary:")
            print("=" * 80)
            print(f"Total Questions: {data.get('total', 0)}")
            
            if data.get('questions'):
                print(f"\nQuestions Found:")
                for i, q in enumerate(data['questions'], 1):
                    print(f"\n  {i}. {q.get('question_text', 'N/A')}")
                    print(f"     - ID: {q.get('question_id')}")
                    print(f"     - Type: {q.get('question_type')}")
                    print(f"     - Dynamic Options: {q.get('dynamic_options', 'None')}")
                    print(f"     - Allow Text: {q.get('allow_text', False)}")
                    if q.get('options'):
                        print(f"     - Options: {len(q['options'])} static options")
        
        elif response.status_code == 401:
            print("\n✗ Authentication required!")
            print("This endpoint requires a valid access token.")
            print("Response:", response.json())
        
        elif response.status_code == 404:
            print("\n✗ Not found!")
            print("No questions found for the specified parameters.")
            print("Response:", response.json())
        
        else:
            print(f"\n✗ Error! Status code: {response.status_code}")
            print("Response:", response.text)
    
    except requests.exceptions.Timeout:
        print("\n✗ Request timed out!")
    
    except requests.exceptions.ConnectionError:
        print("\n✗ Connection error! Could not reach the server.")
    
    except requests.exceptions.RequestException as e:
        print(f"\n✗ Request failed: {e}")
    
    except json.JSONDecodeError:
        print("\n✗ Failed to parse JSON response")
        print("Raw response:", response.text)
    
    print("\n" + "=" * 80)


def test_all_focus_types():
    """Test all focus types"""
    
    url = "https://movokio.com/api/v1/feedback/questions"
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxOCwiZXhwIjoxNzY1MDIxMTQzLCJ0eXBlIjoiYWNjZXNzIn0.P9te4f2-YwlSxuYjgFeY_J3XdrzZKfy9w4Ar7cCOrM4"
    }
    focus_types = ["performance_enhancement", "body_recomposition", "efficiency", "rebuilding_rehab"]
    
    print("\n" + "=" * 80)
    print("Testing All Focus Types")
    print("=" * 80)
    
    for focus in focus_types:
        print(f"\n\nTesting focus: {focus}")
        print("-" * 80)
        
        params = {
            "week_table": "workout_weeks",
            "week_number": 1,
            "focus": focus
        }
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Status: {response.status_code} | Questions found: {data.get('total', 0)}")
            else:
                print(f"✗ Status: {response.status_code} | {response.text[:100]}")
        
        except Exception as e:
            print(f"✗ Error: {e}")


def test_different_weeks():
    """Test different week numbers"""
    
    url = "https://movokio.com/api/v1/feedback/questions"
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxOCwiZXhwIjoxNzY1MDIxMTQzLCJ0eXBlIjoiYWNjZXNzIn0.P9te4f2-YwlSxuYjgFeY_J3XdrzZKfy9w4Ar7cCOrM4"
    }
    
    print("\n" + "=" * 80)
    print("Testing Different Week Numbers")
    print("=" * 80)
    
    for week_num in [1, 4, 8, 12]:
        print(f"\n\nTesting week_number: {week_num}")
        print("-" * 80)
        
        params = {
            "week_table": "workout_weeks",
            "week_number": week_num,
            "focus": "efficiency"
        }
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Status: {response.status_code} | Questions found: {data.get('total', 0)}")
            else:
                print(f"✗ Status: {response.status_code} | {response.text[:100]}")
        
        except Exception as e:
            print(f"✗ Error: {e}")


def test_nutrition_weeks():
    """Test nutrition weeks"""
    
    url = "https://movokio.com/api/v1/feedback/questions"
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxOCwiZXhwIjoxNzY1MDIxMTQzLCJ0eXBlIjoiYWNjZXNzIn0.P9te4f2-YwlSxuYjgFeY_J3XdrzZKfy9w4Ar7cCOrM4"
    }
    
    print("\n" + "=" * 80)
    print("Testing Nutrition Weeks")
    print("=" * 80)
    
    params = {
        "week_table": "nutrition_weeks",
        "week_number": 1,
        "focus": "body_recomposition"
    }
    
    print(f"\nParameters: {json.dumps(params, indent=2)}")
    print("-" * 80)
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✓ Status: {response.status_code}")
            print(f"Total Questions: {data.get('total', 0)}")
            
            if data.get('questions'):
                for i, q in enumerate(data['questions'], 1):
                    print(f"\n  {i}. {q.get('question_text', 'N/A')}")
                    print(f"     - Type: {q.get('question_type')}")
        else:
            print(f"\n✗ Status: {response.status_code}")
            print("Response:", response.text[:200])
    
    except Exception as e:
        print(f"\n✗ Error: {e}")


if __name__ == "__main__":
    # Run main test
    test_feedback_questions()
    
    # Uncomment to run additional tests
    # test_all_focus_types()
    # test_different_weeks()
    # test_nutrition_weeks()
