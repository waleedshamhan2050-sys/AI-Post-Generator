import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
# The API key is automatically loaded from OPENAI_API_KEY environment variable
client = OpenAI()

def load_templates(file_path="templates.json"):
    """
    Loads post templates from a JSON file.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Template file not found at {file_path}")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in template file at {file_path}")
        return {}

def generate_post(topic, template_name, templates, model="gpt-4.1-mini"):
    """
    Generates a post using OpenAI's GPT model based on a given topic and template.
    """
    if template_name not in templates:
        print(f"Error: Template \'{template_name}\' not found.")
        return None

    template = templates[template_name]
    prompt = f"""
    أنت مساعد ذكاء اصطناعي متخصص في توليد منشورات احترافية وجذابة لوسائل التواصل الاجتماعي (واتساب وتليجرام).
    المنشور يجب أن يكون باللغة العربية، موجزاً، جذاباً، ويحتوي على رموز تعبيرية (إيموجي) مناسبة.
    
    الموضوع: {topic}
    النمط/القالب: {template["description"]}
    
    تعليمات إضافية:
    - يجب أن يكون المنشور مناسباً لقنوات واتساب وتليجرام.
    - استخدم أسلوباً ودياً ومحفزاً.
    - أضف دعوة لاتخاذ إجراء (Call to Action) إذا كان القالب يتطلب ذلك.
    - استخدم الرموز التعبيرية بذكاء لزيادة الجاذبية.
    - لا تتجاوز 200 كلمة.
    
    مثال على المنشور المطلوب:
    {template["example"]}
    
    الآن، قم بتوليد منشور جديد بناءً على الموضوع والنمط المحدد:
    """

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "أنت مساعد ذكاء اصطناعي متخصص في توليد منشورات احترافية وجذابة لوسائل التواصل الاجتماعي."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300, # Adjust based on desired post length
            temperature=0.7 # Creativity level
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"An error occurred during AI generation: {e}")
        return None

def save_post_example(post_content, topic, template_name, output_dir="examples"):
    """
    Saves a generated post to a text file in the examples directory.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    file_name = f"{output_dir}/{topic.replace(\' \', \'_\')}_{template_name}.txt"
    try:
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(post_content)
        print(f"Generated post saved to: {file_name}")
    except Exception as e:
        print(f"Error saving post to file: {e}")

def main():
    print("\n--- AI Post Generator ---")
    templates = load_templates()

    if not templates:
        print("No templates loaded. Please check templates.json.")
        return

    print("\nالقوالب المتاحة:")
    for i, (name, data) in enumerate(templates.items()):
        print(f"{i+1}. {name}: {data["description"]}")

    while True:
        topic = input("\nأدخل موضوع المنشور (أو \'خروج\' للإنهاء): ")
        if topic.lower() == \'خروج\':
            break

        template_choice = input("اختر رقم القالب أو اسمه: ")
        selected_template_name = None
        try:
            idx = int(template_choice) - 1
            if 0 <= idx < len(templates):
                selected_template_name = list(templates.keys())[idx]
        except ValueError:
            if template_choice in templates:
                selected_template_name = template_choice
        
        if not selected_template_name:
            print("اختيار قالب غير صالح. يرجى المحاولة مرة أخرى.")
            continue

        print(f"\nجاري توليد منشور حول \'{topic}\' باستخدام قالب \'{selected_template_name}\'...")
        generated_post = generate_post(topic, selected_template_name, templates)

        if generated_post:
            print("\n--- المنشور المولد ---")
            print(generated_post)
            print("----------------------")
            save_post_example(generated_post, topic, selected_template_name)
        else:
            print("فشل توليد المنشور.")

if __name__ == "__main__":
    main()
