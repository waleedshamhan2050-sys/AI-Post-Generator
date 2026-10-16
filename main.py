import os
import json
import argparse
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_client(provider):
    """
    Returns an OpenAI-compatible client for the chosen provider.

    - "openai": the hosted OpenAI API (needs OPENAI_API_KEY).
    - "ollama": a local Ollama server running an open-weight model.
      Ollama exposes an OpenAI-compatible API, so the same client
      works — only the base URL and model name change.
      No API key is needed locally; "ollama" is a placeholder.
    """
    if provider == "ollama":
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
        # The Ollama client only ever talks to localhost, so proxies are
        # irrelevant — and a malformed proxy variable in the environment
        # can break client creation. Clear proxy settings for this
        # process-local client and force localhost to bypass proxies.
        for var in ("HTTP_PROXY", "http_proxy", "HTTPS_PROXY", "https_proxy",
                    "ALL_PROXY", "all_proxy"):
            os.environ.pop(var, None)
        os.environ["NO_PROXY"] = "localhost,127.0.0.1"
        os.environ["no_proxy"] = "localhost,127.0.0.1"
        return OpenAI(base_url=base_url, api_key="ollama")
    return OpenAI()


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


def build_prompt(topic, template):
    """Builds the post-generation prompt from a topic and a template."""
    return f"""
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


def generate_post(topic, template_name, templates, provider="ollama", model=None):
    """
    Generates a post using the chosen provider based on a topic and template.

    - provider="ollama" (default): local open-weight model via Ollama.
      Default model is Gemma 3 (open-weight), override with
      OLLAMA_MODEL in .env or --model on the command line.
    - provider="openai": hosted OpenAI API, default model gpt-4.1-mini.
    """
    if template_name not in templates:
        print(f"Error: Template '{template_name}' not found.")
        return None

    if provider == "ollama":
        model = model or os.getenv("OLLAMA_MODEL", "gemma3")
    else:
        model = model or "gpt-4.1-mini"

    client = get_client(provider)
    prompt = build_prompt(topic, templates[template_name])

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "أنت مساعد ذكاء اصطناعي متخصص في توليد منشورات احترافية وجذابة لوسائل التواصل الاجتماعي."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,  # Adjust based on desired post length
            temperature=0.7  # Creativity level
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

    file_name = f"{output_dir}/{topic.replace(' ', '_')}_{template_name}.txt"
    try:
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(post_content)
        print(f"Generated post saved to: {file_name}")
    except Exception as e:
        print(f"Error saving post to file: {e}")


def main():
    parser = argparse.ArgumentParser(description="AI Post Generator — WhatsApp & Telegram posts")
    parser.add_argument("--provider", choices=["ollama", "openai"], default="ollama",
                        help="Model provider: 'ollama' = local open-weight model (default), 'openai' = hosted OpenAI API")
    parser.add_argument("--model", default=None,
                        help="Model name (default: OLLAMA_MODEL env or 'gemma3' for ollama, 'gpt-4.1-mini' for openai)")
    args = parser.parse_args()

    print("\n--- AI Post Generator ---")
    print(f"Provider: {args.provider} | Model: {args.model or os.getenv('OLLAMA_MODEL', 'gemma3') if args.provider == 'ollama' else args.model or 'gpt-4.1-mini'}")
    templates = load_templates()

    if not templates:
        print("No templates loaded. Please check templates.json.")
        return

    print("\nالقوالب المتاحة:")
    for i, (name, data) in enumerate(templates.items()):
        print(f"{i+1}. {name}: {data['description']}")

    while True:
        topic = input("\nأدخل موضوع المنشور (أو 'خروج' للإنهاء): ")
        if topic.lower() == 'خروج':
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

        print(f"\nجاري توليد منشور حول '{topic}' باستخدام قالب '{selected_template_name}'...")
        generated_post = generate_post(topic, selected_template_name, templates,
                                       provider=args.provider, model=args.model)

        if generated_post:
            print("\n--- المنشور المولد ---")
            print(generated_post)
            print("----------------------")
            save_post_example(generated_post, topic, selected_template_name)
        else:
            print("فشل توليد المنشور.")


if __name__ == "__main__":
    main()
