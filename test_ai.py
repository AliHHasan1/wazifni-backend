import os
from dotenv import load_dotenv
from services.ai_service import GeminiAIService

# تحميل المتغيرات من ملف .env
load_dotenv()


def test_gemini():
    print("--- جاري اختبار الاتصال بـ Gemini API ---")
    try:
        service = GeminiAIService()
        test_text = "أنا عملت مبرمج في شركة طبية لمدة سنتين وقمت بتطوير تطبيقات أندرويد."
        print(f"النص الأصلي: {test_text}")

        enhanced = service.enhance_text(test_text)

        print("\n--- النتيجة من الذكاء الاصطناعي ---")
        print(enhanced)
        print("\n--- تم الاختبار بنجاح! ---")
    except Exception as e:
        print(f"\n❌ حدث خطأ أثناء الاختبار: {e}")


if __name__ == "__main__":
    test_gemini()
