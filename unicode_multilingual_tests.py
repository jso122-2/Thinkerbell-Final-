#!/usr/bin/env python3
"""
🌍 Unicode and Multilingual Testing Suite for Thinkerbell Model
=============================================================

This suite tests the model's handling of:
1. Unicode characters and emojis
2. Multiple languages and scripts
3. Right-to-left (RTL) languages
4. Mixed script content
5. Unicode normalization issues
6. Character encoding edge cases
"""

import requests
import json
import unicodedata
import sys
from typing import Dict, List, Any

API_BASE_URL = "http://localhost:8000"

class UnicodeMultilingualTester:
    """Test Unicode and multilingual capabilities"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.results = []
    
    def test_unicode_case(self, name: str, input_text: str, description: str = "") -> Dict[str, Any]:
        """Test a single Unicode case"""
        print(f"\n🌍 Testing: {name}")
        if description:
            print(f"   Description: {description}")
        
        input_data = {
            "human_example": input_text,
            "target_length": 700,
            "style_preference": "professional",
            "document_type": "legal_template"
        }
        
        try:
            response = requests.post(f"{self.base_url}/generate", json=input_data, timeout=30)
            
            result = {
                "test_name": name,
                "input_text": input_text,
                "input_length": len(input_text),
                "input_byte_length": len(input_text.encode('utf-8')),
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "unicode_analysis": self.analyze_unicode(input_text)
            }
            
            if response.status_code == 200:
                data = response.json()
                generated_text = data.get("generated_text", "")
                
                result.update({
                    "generated_text": generated_text,
                    "output_length": len(generated_text),
                    "output_byte_length": len(generated_text.encode('utf-8')),
                    "similarity_score": data.get("similarity_to_example", 0),
                    "word_count": data.get("word_count", 0),
                    "processing_time": data.get("processing_time", 0),
                    "output_unicode_analysis": self.analyze_unicode(generated_text)
                })
                
                # Check if output is reasonable
                if len(generated_text.strip()) < 50:
                    result["warning"] = "Generated text is very short"
                
                print(f"   ✅ Success: {len(generated_text)} chars generated")
                print(f"   Similarity: {data.get('similarity_to_example', 0):.3f}")
                
            else:
                result["error"] = response.text[:200]
                print(f"   ❌ Failed: HTTP {response.status_code}")
            
            self.results.append(result)
            return result
            
        except Exception as e:
            result = {
                "test_name": name,
                "input_text": input_text,
                "success": False,
                "error": str(e),
                "unicode_analysis": self.analyze_unicode(input_text)
            }
            self.results.append(result)
            print(f"   ❌ Exception: {str(e)}")
            return result
    
    def analyze_unicode(self, text: str) -> Dict[str, Any]:
        """Analyze Unicode properties of text"""
        if not text:
            return {"empty": True}
        
        analysis = {
            "length": len(text),
            "byte_length": len(text.encode('utf-8')),
            "categories": {},
            "scripts": {},
            "has_emojis": False,
            "has_rtl": False,
            "normalization_forms": {}
        }
        
        # Analyze character categories and scripts
        for char in text:
            category = unicodedata.category(char)
            analysis["categories"][category] = analysis["categories"].get(category, 0) + 1
            
            try:
                script = unicodedata.name(char).split()[0] if unicodedata.name(char) else "UNKNOWN"
                analysis["scripts"][script] = analysis["scripts"].get(script, 0) + 1
            except ValueError:
                analysis["scripts"]["UNNAMED"] = analysis["scripts"].get("UNNAMED", 0) + 1
            
            # Check for emojis (simplified check)
            if ord(char) >= 0x1F600 and ord(char) <= 0x1F64F:  # Emoticons
                analysis["has_emojis"] = True
            elif ord(char) >= 0x1F300 and ord(char) <= 0x1F5FF:  # Misc Symbols
                analysis["has_emojis"] = True
            elif ord(char) >= 0x1F680 and ord(char) <= 0x1F6FF:  # Transport
                analysis["has_emojis"] = True
            elif ord(char) >= 0x2600 and ord(char) <= 0x26FF:    # Misc symbols
                analysis["has_emojis"] = True
            
            # Check for RTL characters
            if unicodedata.bidirectional(char) in ['R', 'AL']:
                analysis["has_rtl"] = True
        
        # Check normalization forms
        try:
            analysis["normalization_forms"] = {
                "NFC": unicodedata.normalize('NFC', text) == text,
                "NFD": unicodedata.normalize('NFD', text) == text,
                "NFKC": unicodedata.normalize('NFKC', text) == text,
                "NFKD": unicodedata.normalize('NFKD', text) == text
            }
        except Exception:
            analysis["normalization_forms"] = {"error": "Could not check normalization"}
        
        return analysis
    
    def run_unicode_tests(self) -> List[Dict[str, Any]]:
        """Run comprehensive Unicode tests"""
        print("🌍 UNICODE & MULTILINGUAL TEST SUITE")
        print("=" * 50)
        
        # Test 1: Basic Emoji Usage
        self.test_unicode_case(
            "Basic Emojis",
            "I need a contract 📝 for social media marketing 📱. The influencer will post content 📸 and we'll pay them money 💰. This should be fun! 🎉",
            "Test basic emoji handling"
        )
        
        # Test 2: Emoji Overload
        self.test_unicode_case(
            "Emoji Overload",
            "🎉🚀💼📝✨🤝💰📱📸🎬🎭🌟💯🔥⭐🎯🏆💎🎪🎨🎵🎮🎲🎳🎯 Contract for influencer! 🎉🚀💼📝✨🤝💰📱📸🎬🎭🌟💯🔥⭐🎯🏆💎🎪🎨🎵🎮🎲🎳🎯",
            "Test excessive emoji usage"
        )
        
        # Test 3: Spanish
        self.test_unicode_case(
            "Spanish Text",
            "Necesito un contrato para marketing de influencers en redes sociales. El influencer publicará contenido sobre nuestros productos de belleza en Instagram y TikTok. El pago será de $5000 más productos gratuitos. La colaboración durará 3 meses con exclusividad en la categoría de belleza.",
            "Test Spanish language processing"
        )
        
        # Test 4: French with Accents
        self.test_unicode_case(
            "French with Accents",
            "J'ai besoin d'un contrat pour le marketing d'influence sur les réseaux sociaux. L'influenceur créera du contenu authentique pour notre marque de cosmétiques. La rémunération comprend un paiement fixe et une commission sur les ventes générées.",
            "Test French with accent marks"
        )
        
        # Test 5: German with Umlauts
        self.test_unicode_case(
            "German with Umlauts",
            "Ich benötige einen Vertrag für Influencer-Marketing in sozialen Medien. Der Influencer wird über unsere Schönheitsprodukte posten und dafür bezahlt werden. Die Zusammenarbeit soll professionell und authentisch sein.",
            "Test German umlauts (ä, ö, ü, ß)"
        )
        
        # Test 6: Russian Cyrillic
        self.test_unicode_case(
            "Russian Cyrillic",
            "Мне нужен контракт для маркетинга в социальных сетях. Инфлюенсер будет публиковать контент о наших продуктах красоты в Instagram и TikTok. Оплата составит $3000 плюс бесплатные продукты.",
            "Test Cyrillic script"
        )
        
        # Test 7: Arabic (RTL)
        self.test_unicode_case(
            "Arabic RTL",
            "أحتاج إلى عقد للتسويق عبر وسائل التواصل الاجتماعي. سيقوم المؤثر بنشر محتوى عن منتجات الجمال الخاصة بنا على إنستغرام وتيك توك. الدفع سيكون ٥٠٠٠ دولار بالإضافة إلى منتجات مجانية.",
            "Test Arabic right-to-left script"
        )
        
        # Test 8: Hebrew (RTL)
        self.test_unicode_case(
            "Hebrew RTL",
            "אני צריך חוזה לשיווק ברשתות החברתיות. המשפיען יפרסם תוכן על מוצרי היופי שלנו באינסטגרם ובטיקטוק. התשלום יהיה ₪15,000 בתוספת מוצרים חינם.",
            "Test Hebrew right-to-left script"
        )
        
        # Test 9: Japanese (Mixed Scripts)
        self.test_unicode_case(
            "Japanese Mixed Scripts",
            "インフルエンサーマーケティングの契約が必要です。インフルエンサーは私たちの美容製品についてInstagramとTikTokに投稿します。報酬は$5000と無料製品です。3ヶ月間の独占契約です。",
            "Test Japanese with Hiragana, Katakana, and Kanji"
        )
        
        # Test 10: Chinese Simplified
        self.test_unicode_case(
            "Chinese Simplified",
            "我需要一份社交媒体影响者营销合同。影响者将在Instagram和TikTok上发布关于我们美容产品的内容。报酬是5000美元加免费产品。合作期为3个月，在美容类别中具有独家性。",
            "Test Simplified Chinese characters"
        )
        
        # Test 11: Chinese Traditional
        self.test_unicode_case(
            "Chinese Traditional",
            "我需要一份社交媒體影響者營銷合同。影響者將在Instagram和TikTok上發布關於我們美容產品的內容。報酬是5000美元加免費產品。合作期為3個月，在美容類別中具有獨家性。",
            "Test Traditional Chinese characters"
        )
        
        # Test 12: Korean
        self.test_unicode_case(
            "Korean Hangul",
            "소셜 미디어 인플루언서 마케팅 계약이 필요합니다. 인플루언서는 Instagram과 TikTok에서 우리 뷰티 제품에 대한 콘텐츠를 게시할 것입니다. 보상은 $5000와 무료 제품입니다.",
            "Test Korean Hangul script"
        )
        
        # Test 13: Thai
        self.test_unicode_case(
            "Thai Script",
            "ฉันต้องการสัญญาสำหรับการตลาดผ่านอินฟลูเอนเซอร์ในโซเชียลมีเดีย อินฟลูเอนเซอร์จะโพสต์เนื้อหาเกี่ยวกับผลิตภัณฑ์ความงามของเราใน Instagram และ TikTok",
            "Test Thai script with complex characters"
        )
        
        # Test 14: Hindi Devanagari
        self.test_unicode_case(
            "Hindi Devanagari",
            "मुझे सोशल मीडिया इन्फ्लुएंसर मार्केटिंग के लिए एक अनुबंध चाहिए। इन्फ्लुएंसर Instagram और TikTok पर हमारे ब्यूटी प्रोडक्ट्स के बारे में कंटेंट पोस्ट करेगा।",
            "Test Hindi Devanagari script"
        )
        
        # Test 15: Mixed Languages
        self.test_unicode_case(
            "Mixed Languages",
            "I need a contrato for marketing en español, français, and 中文. The influencer will post contenido on Instagram y TikTok about notre produits de beauté 美容产品.",
            "Test mixed language input"
        )
        
        # Test 16: Unicode Control Characters
        self.test_unicode_case(
            "Unicode Control Characters",
            f"Contract\u0000with\u0001control\u0002characters\u0003and\u0004zero\u0005width\u200B\u200C\u200D\uFEFFspaces",
            "Test Unicode control and zero-width characters"
        )
        
        # Test 17: Combining Characters
        self.test_unicode_case(
            "Combining Characters",
            "Contract with combining characters: é (e + ́), ñ (n + ̃), ü (u + ̈), å (a + ̊)",
            "Test combining diacritical marks"
        )
        
        # Test 18: Surrogate Pairs
        self.test_unicode_case(
            "Surrogate Pairs",
            "Contract with surrogate pairs: 𝕋𝕙𝕚𝕤 𝕚𝕤 𝕞𝕒𝕥𝕙𝕖𝕞𝕒𝕥𝕚𝕔𝕒𝕝 𝕕𝕠𝕦𝕓𝕝𝕖-𝕤𝕥𝕣𝕦𝕔𝕜 𝕔𝕙𝕒𝕣𝕒𝕔𝕥𝕖𝕣𝕤 🎭🎪🎨",
            "Test Unicode surrogate pairs (high/low surrogates)"
        )
        
        # Test 19: Normalization Issues
        text_nfc = "café"  # NFC normalized
        text_nfd = "cafe\u0301"  # NFD normalized (e + combining acute)
        self.test_unicode_case(
            "Normalization NFC vs NFD",
            f"Contract for {text_nfc} and {text_nfd} - these should look the same but have different Unicode representations",
            "Test Unicode normalization differences"
        )
        
        # Test 20: Bidirectional Text (Mixed LTR/RTL)
        self.test_unicode_case(
            "Bidirectional Text",
            "Contract between Company Inc. and شركة التسويق الرقمي for marketing campaign on Instagram و TikTok with payment of $5000 و منتجات مجانية",
            "Test mixed left-to-right and right-to-left text"
        )
        
        return self.results
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate test summary"""
        if not self.results:
            return {"error": "No test results available"}
        
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r.get("success", False))
        failed_tests = total_tests - successful_tests
        
        # Analyze Unicode categories tested
        categories_tested = set()
        scripts_tested = set()
        
        for result in self.results:
            if "unicode_analysis" in result:
                analysis = result["unicode_analysis"]
                if "categories" in analysis:
                    categories_tested.update(analysis["categories"].keys())
                if "scripts" in analysis:
                    scripts_tested.update(analysis["scripts"].keys())
        
        summary = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "success_rate": (successful_tests / total_tests * 100) if total_tests > 0 else 0,
            "unicode_categories_tested": len(categories_tested),
            "scripts_tested": len(scripts_tested),
            "categories": sorted(list(categories_tested)),
            "scripts": sorted(list(scripts_tested))
        }
        
        return summary

def main():
    """Main test runner"""
    # Check server connection
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ Server not ready: {response.status_code}")
            sys.exit(1)
        print("✅ Server connection verified")
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to server at {API_BASE_URL}")
        print("Make sure the backend server is running: python backend_api_server.py")
        sys.exit(1)
    
    # Run tests
    tester = UnicodeMultilingualTester()
    results = tester.run_unicode_tests()
    
    # Generate and display summary
    summary = tester.generate_summary()
    
    print("\n" + "=" * 50)
    print("📊 UNICODE & MULTILINGUAL TEST SUMMARY")
    print("=" * 50)
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Successful: {summary['successful_tests']} ✅")
    print(f"Failed: {summary['failed_tests']} ❌")
    print(f"Success Rate: {summary['success_rate']:.1f}%")
    print(f"Unicode Categories Tested: {summary['unicode_categories_tested']}")
    print(f"Scripts Tested: {summary['scripts_tested']}")
    
    if summary['failed_tests'] > 0:
        print("\n❌ FAILED TESTS:")
        for result in results:
            if not result.get("success", False):
                print(f"  - {result['test_name']}")
                if "error" in result:
                    print(f"    Error: {result['error']}")
    
    # Save detailed results
    import time
    timestamp = int(time.time())
    filename = f"unicode_test_results_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            "summary": summary,
            "detailed_results": results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Detailed results saved to: {filename}")

if __name__ == "__main__":
    main()
