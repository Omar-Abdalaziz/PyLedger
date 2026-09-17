# 📊 PyLedger - مكتبة محاسبة احترافية لـ Python

## نظرة عامة

**PyLedger** هي مكتبة Python احترافية وشاملة لبناء الأنظمة المحاسبية والمالية. توفر كل ما تحتاجه لإنشاء:

- 📊 **أنظمة محاسبة متقدمة**
- 📄 **برامج إدارة الفواتير**
- 🏢 **أنظمة ERP بسيطة**
- 💸 **تطبيقات إدارة المصروفات**
- 📈 **أنظمة مالية متخصصة**

**بدون الحاجة لكتابة المنطق المحاسبي من الصفر!**

---

## ✨ الميزات الرئيسية

### 1. 📝 إدارة دفتر الحسابات
- حسابات مالية متعددة الأنواع
- دفتر حسابات متكامل
- تتبع المعاملات بشكل آلي
- التوازن التلقائي للقيود

### 2. 📋 القيود اليومية
- تسجيل المعاملات المحاسبية
- التحقق من التوازن تلقائياً
- سجل كامل للمعاملات
- ترحيل آمن للدفتر

### 3. 📄 إدارة الفواتير
- إنشاء وإدارة الفواتير
- تتبع الدفع بسهولة
- دعم ضرائب متعددة
- معالجة الأرصدة المدفوعة

### 4. 💰 إدارة الضرائب
- حساب الضريبة المضافة (VAT)
- ضرائب متعددة في الفاتورة الواحدة
- حسابات عكسية للضرائب
- معايير ضريبية مرنة

### 5. 💱 دعم العملات
- دعم 8 عملات عالمية
- تحويل سهل بين العملات
- عمليات حسابية آمنة على المال
- معدلات صرف قابلة للتحديث

### 6. 📊 التقارير المالية
- **قائمة الدخل** (Income Statement)
- **الميزانية العمومية** (Balance Sheet)
- **بيان التدفقات النقدية** (Cash Flow)
- **ميزان المراجعة** (Trial Balance)

### 7. 🗄️ دعم قواعد البيانات
- SQLite المدمج
- دعم PostgreSQL و MySQL (جاهز)
- نمط Repository للمرونة
- ORM الجاهزية

### 8. ✅ التحقق الشامل
- التحقق من صيغة الحساب
- التحقق من المبالغ المالية
- التحقق من العملات
- التحقق من معدلات الضريبة

### 9. 🔒 معالجة الأخطاء
- استثناءات مخصصة للعمليات المحاسبية
- رسائل خطأ واضحة
- التحقق من التوازن
- الحماية من الأخطاء الحسابية

---

## 🏗️ هيكل المكتبة

```
pyledger/
├── core/                          # المكونات الأساسية
│   ├── __init__.py
│   ├── account.py                 # إدارة الحسابات
│   ├── ledger.py                  # دفتر الحسابات
│   ├── transaction.py             # المعاملات
│   └── journal.py                 # القيود اليومية
│
├── accounting/                    # العمليات المحاسبية
│   ├── __init__.py
│   ├── invoice.py                 # إدارة الفواتير
│   ├── tax.py                     # إدارة الضرائب
│   └── payment.py                 # معالجة الدفعات
│
├── reports/                       # التقارير المالية
│   ├── __init__.py
│   ├── balance_sheet.py           # الميزانية والدخل والتدفق
│   ├── income_statement.py        # قائمة الدخل
│   └── cash_flow.py               # بيان التدفقات
│
├── database/                      # طبقة قاعدة البيانات
│   ├── __init__.py
│   ├── models.py                  # نماذج البيانات
│   └── repository.py              # نمط Repository
│
├── utils/                         # أدوات مساعدة
│   ├── __init__.py
│   ├── validators.py              # دوال التحقق
│   ├── currency.py                # إدارة العملات
│   └── formatter.py               # تنسيق البيانات
│
├── exceptions/                    # الاستثناءات
│   ├── __init__.py
│   └── errors.py                  # تعريفات الأخطاء
│
├── __init__.py                    # نقطة الدخول الرئيسية
├── setup.py                       # إعدادات التثبيت
├── config.py                      # ملف الإعدادات
├── example.py                     # مثال عملي شامل
├── test_pyledger.py              # اختبارات شاملة
├── README.md                      # التوثيق الكامل
├── QUICKSTART.md                  # دليل البدء السريع
├── EXAMPLES.md                    # أمثلة متقدمة
├── CHANGELOG.md                   # سجل التغييرات
├── LICENSE                        # الترخيص (Apache-2.0)
└── .gitignore                     # ملف Git Ignore
```

---

## 🚀 البدء السريع

### التثبيت

```bash
pip install pyledger
```

أو من المصدر:
```bash
git clone <repository-url>
cd pyledger
pip install -e .
```

### مثال بسيط

```python
from pyledger import Ledger, Account, JournalEntry

# إنشاء دفتر حسابات
ledger = Ledger("شركتي", currency="SAR")

# إنشاء حسابات
cash = Account("النقدية", "asset", "1000")
sales = Account("المبيعات", "income", "4000")

# إضافة الحسابات
ledger.add_account(cash)
ledger.add_account(sales)

# تسجيل معاملة
entry = JournalEntry("مبيعات اليوم")
entry.add_debit(cash, 1000)
entry.add_credit(sales, 1000)
entry.post()

ledger.record_entry(entry)

# عرض ميزان المراجعة
print(ledger.get_trial_balance())
```

---

## 📚 الفئات الأساسية

### 1️⃣ Account (الحساب)

يمثل حساباً محاسبياً في النظام.

```python
account = Account(
    name="النقدية",           # اسم الحساب
    account_type="asset",      # نوع الحساب
    code="1000-CASH",          # رمز الحساب
    currency="SAR",            # العملة
    description="رصيد النقد"   # الوصف
)

# إضافة مبلغ
account.deposit(1000, "إيداع نقدي")

# سحب مبلغ
account.withdraw(500, "مصروف نقدي")

# الحصول على الرصيد
balance = account.get_balance()
```

**أنواع الحسابات:**
- `asset` 💰 - الأصول (نقد، مستثمرات، ممتلكات)
- `liability` 📊 - الالتزامات (قروض، حسابات دائنة)
- `equity` 📈 - حقوق الملكية (رأس المال)
- `income` 💵 - الإيرادات (مبيعات، فوائد)
- `expense` 📉 - المصروفات (رواتب، إيجار)

### 2️⃣ Ledger (دفتر الحسابات)

يدير جميع الحسابات والمعاملات.

```python
ledger = Ledger("دفتري الرئيسي", currency="SAR")

# إضافة حساب
ledger.add_account(account)

# الحصول على حساب
account = ledger.get_account("1000-CASH")

# تحويل بين حسابين
ledger.transfer(from_account, to_account, 500)

# الحصول على ميزان المراجعة
trial_balance = ledger.get_trial_balance()

# ملخصات مالية
total_assets = ledger.get_total_assets()
total_expenses = ledger.get_total_expenses()
```

### 3️⃣ JournalEntry (القيد اليومي)

تسجيل معاملة محاسبية متوازنة.

```python
entry = JournalEntry("معاملة البيع")

# إضافة طرف مدين (Debit)
entry.add_debit(cash, 1000, "نقد استلام")

# إضافة طرف دائن (Credit)
entry.add_credit(sales, 1000, "إيراد معترف به")

# التحقق من التوازن
if entry.is_balanced():
    entry.post()

# تسجيل في الدفتر
ledger.record_entry(entry)
```

### 4️⃣ Invoice (الفاتورة)

إدارة الفواتير والدفعات.

```python
invoice = Invoice("اسم العميل", currency="SAR")

# إضافة بنود
invoice.add_item("منتج 1", quantity=2, unit_price=500)
invoice.add_item("خدمة", quantity=1, unit_price=1000)

# إضافة ضريبة
vat = Tax("ضريبة القيمة المضافة", 15)
invoice.add_tax(vat)

# إصدار الفاتورة
invoice.issue()

# تسجيل الدفع
invoice.pay(amount=2000, method='bank_transfer')

# معلومات الفاتورة
print(f"الرصيد المتبقي: {invoice.get_remaining_balance()}")
```

### 5️⃣ Tax (الضريبة)

حساب الضرائب المختلفة.

```python
# إنشاء ضريبة
vat = Tax("ضريبة القيمة المضافة", 15)

# حساب مبلغ الضريبة
tax_amount = vat.calculate(1000)  # 150

# حساب الإجمالي مع الضريبة
total = vat.calculate_total(1000)  # 1150

# حساب VAT بشكل مباشر
result = Tax.calculate_vat(1000, 15)
# {'base': 1000, 'vat_amount': 150, 'total': 1150}

# حساب الأساس من الإجمالي (عكسي)
result = Tax.reverse_calculate(1150, 15)
# {'base': 1000, 'tax_amount': 150, 'total': 1150}
```

### 6️⃣ Reports (التقارير)

إنشاء التقارير المالية.

```python
from pyledger import IncomeStatement, BalanceSheet, CashFlowStatement

# قائمة الدخل
income_stmt = IncomeStatement(ledger)
income_data = income_stmt.generate()
print(income_stmt)

# الميزانية العمومية
balance_sheet = BalanceSheet(ledger)
balance_data = balance_sheet.generate()
print(balance_sheet)

# بيان التدفقات النقدية
cash_flow = CashFlowStatement(ledger)
cash_flow_data = cash_flow.generate()
```

---

## 💡 أمثلة عملية

### مثال 1: نظام محاسبة بسيط

```python
from pyledger import *

# إنشاء الدفتر
ledger = Ledger("شركة المثال", currency="SAR")

# إنشاء الحسابات
accounts = {
    "1000": ("النقدية", "asset"),
    "4000": ("المبيعات", "income"),
    "5000": ("المصروفات", "expense"),
    "3000": ("رأس المال", "equity"),
}

for code, (name, acc_type) in accounts.items():
    account = Account(name, acc_type, code)
    ledger.add_account(account)

# رصيد افتتاحي
opening = JournalEntry("الرصيد الافتتاحي")
opening.add_debit(ledger.get_account("1000"), 100000)
opening.add_credit(ledger.get_account("3000"), 100000)
opening.post()
ledger.record_entry(opening)

# مبيعات
sales = JournalEntry("المبيعات")
sales.add_debit(ledger.get_account("1000"), 50000)
sales.add_credit(ledger.get_account("4000"), 50000)
sales.post()
ledger.record_entry(sales)

# المصروفات
expense = JournalEntry("المصروفات")
expense.add_debit(ledger.get_account("5000"), 10000)
expense.add_credit(ledger.get_account("1000"), 10000)
expense.post()
ledger.record_entry(expense)
```

### مثال 2: نظام الفواتير

```python
# إنشاء فاتورة
invoice = Invoice("شركة ABC", currency="SAR")

# إضافة بنود
items = [
    ("استشارات", 10, 500),
    ("برنامج", 1, 5000),
    ("دعم فني", 5, 200),
]

for item_name, qty, price in items:
    invoice.add_item(item_name, qty, price)

# إضافة ضريبة 15%
vat = Tax("ضريبة القيمة المضافة", 15)
invoice.add_tax(vat)

# معالجة الدفع
invoice.issue()
invoice.pay(5000, method='bank_transfer')
invoice.pay(3000, method='check')

# الحصول على التفاصيل
print(f"الإجمالي: {invoice.total}")
print(f"المدفوع: {invoice.paid_amount}")
print(f"المتبقي: {invoice.get_remaining_balance()}")
```

---

## 🧪 الاختبار

```bash
# تثبيت متطلبات التطوير
pip install -r requirements-dev.txt

# تشغيل الاختبارات
pytest test_pyledger.py -v

# تشغيل مثال العمل
python example.py
```

---

## 📖 المزيد من المعلومات

- 📘 **[دليل البدء السريع](QUICKSTART.md)** - شروع سريع
- 📗 **[أمثلة متقدمة](EXAMPLES.md)** - حالات استخدام متقدمة
- 📕 **[سجل التغييرات](CHANGELOG.md)** - آخر التحديثات

---

## 🔒 معالجة الأخطاء

```python
from pyledger import *

try:
    # محاولة الحصول على حساب غير موجود
    account = ledger.get_account("INVALID")
except AccountNotFoundError:
    print("الحساب غير موجود")

try:
    # محاولة سحب أكثر من الرصيد
    account.withdraw(10000)
except InsufficientBalanceError:
    print("رصيد غير كافي")

try:
    # قيد غير متوازن
    entry = JournalEntry("معاملة")
    entry.add_debit(account1, 100)
    entry.add_credit(account2, 50)  # غير متساوي!
    entry.post()
except UnbalancedEntryError:
    print("القيد غير متوازن")
```

---

## 🌍 العملات المدعومة

| الرمز | العملة | الدول |
|------|--------|-------|
| USD | الدولار الأمريكي | أمريكا |
| EUR | اليورو | أوروبا |
| GBP | الجنيه الاسترليني | بريطانيا |
| SAR | الريال السعودي | السعودية |
| AED | درهم إماراتي | الإمارات |
| EGP | الجنيه المصري | مصر |
| JOD | الدينار الأردني | الأردن |
| KWD | الدينار الكويتي | الكويت |

---

## ✅ أفضل الممارسات

1. ✓ تحقق من صحة البيانات قبل الإدخال
2. ✓ تأكد من توازن القيود قبل الترحيل
3. ✓ استخدم رموز حسابات واضحة ومنتظمة
4. ✓ سجل المعاملات فوراً
5. ✓ راجع القوائم المالية بانتظام
6. ✓ احتفظ بسجل تدقيق كامل
7. ✓ استخدم أسماء وصفية للمعاملات

---

## 📝 الترخيص

هذا المشروع مرخص تحت رخصة Apache-2.0 - انظر ملفي [LICENSE](LICENSE) و NOTICE للتفاصيل.

---

## 🤝 المساهمة

نرحب بالمساهمات! الرجاء:
1. عمل Fork للمشروع
2. إنشاء فرع جديد للميزة
3. إرسال Pull Request

---

## 📞 الدعم

للإبلاغ عن مشاكل أو اقتراح ميزات جديدة:
- 📧 البريد الإلكتروني: support@pyledger.dev
- 🐛 GitHub Issues: [Report a bug](https://github.com/yourusername/pyledger/issues)

---

## 🎯 خارطة الطريق

- ✅ الإصدار الأول (v1.0.0)
- 🔄 دعم ORM كامل (v1.1.0)
- 🔄 واجهة REST API (v1.2.0)
- 🔄 إنشاء PDF للفواتير (v1.3.0)
- 🔄 نسب مالية متقدمة (v1.4.0)
- 🔄 إدارة الموازنات (v2.0.0)

---

## ✨ شكر خاص

تم بناء هذه المكتبة بعناية فائقة لتوفير حل محاسبي احترافي وموثوق للمبرمجين.

---

**صُنع بـ ❤️ من قبل فريق PyLedger**

**الإصدار:** 1.0.0  
**آخر تحديث:** مارس 2026
