# PyLedger 📊

**Professional Accounting Library for Python**

PyLedger هي مكتبة Python احترافية لبناء الأنظمة المحاسبية والمالية دون الحاجة لكتابة المنطق المحاسبي من الصفر.

> النسخة الإنجليزية الكاملة والمرجع الشامل لكل الدوال في [README.md](README.md).

## ✨ الميزات الرئيسية

- 📝 **دفتر الحسابات** - إدارة حسابات مالية احترافية
- 📋 **القيود اليومية** - تسجيل المعاملات المحاسبية مع التوازن التلقائي
- 📄 **الفواتير والمدفوعات** - نظام إدارة فواتير متكامل
- 💰 **إدارة الضرائب** - حساب الضريبة المضافة والضرائب المختلفة
- 💱 **دعم العملات** - دعم عملات متعددة وتحويل العملات
- 📊 **التقارير المالية** - ميزانية عمومية، قائمة الدخل، التدفقات النقدية
- 🗄️ **قواعد البيانات** - دعم SQLite و PostgreSQL و MySQL
- ✅ **التحقق من البيانات** - نظام شامل للتحقق من صحة البيانات

## 📦 التثبيت

```bash
pip install pyledger
```

أو من المصدر:

```bash
git clone https://github.com/<your-username>/pyledger.git
cd pyledger
pip install -e .
```

## 🚀 البدء السريع

### مثال بسيط

```python
from pyledger import Ledger, Account, JournalEntry

# إنشاء دفتر حسابات
ledger = Ledger("Main Ledger", currency="USD")

# إنشاء حسابات
cash = Account("Cash", "asset", "1000-CASH")
sales = Account("Sales Revenue", "income", "4000-SALES")

# إضافة الحسابات للدفتر
ledger.add_account(cash)
ledger.add_account(sales)

# إنشاء قيد يومي
entry = JournalEntry("First sale of the year")
entry.add_debit(cash, 1000, "Cash receipt from sale")
entry.add_credit(sales, 1000, "Revenue from sale")
entry.post()

ledger.record_entry(entry)

# طباعة ميزان المراجعة
print(ledger.get_trial_balance())
```

### مثال متقدم - الفواتير والضرائب

```python
from pyledger import Invoice, Tax, Ledger

# إنشاء فاتورة
invoice = Invoice("Ahmed Trading Company", currency="SAR")

# إضافة بنود الفاتورة
invoice.add_item("منتج 1", quantity=2, unit_price=500)
invoice.add_item("خدمة استشارية", quantity=1, unit_price=1000)

# إضافة ضريبة القيمة المضافة (15%)
vat = Tax("VAT", rate=15)
invoice.add_tax(vat)

# إصدار الفاتورة
invoice.issue()

# تسجيل الدفع
invoice.pay(amount=2500, method='bank_transfer')

print(invoice)
```

### مثال بلغة الأعمال (بدون معرفة محاسبية)

```python
from pyledger import PyLedger

app = PyLedger(company="شركتي", currency="SAR")
app.add_investment("المالك", 100000)
app.sell([{"name": "منتج", "quantity": 2, "price": 500}], customer="C-1")
app.pay_expense("إيجار", 2000, category="rent")
print(app.balance_sheet().generate()["total_assets"])
```

## 📚 الهيكل الأساسي

### الفئات الأساسية

#### 1. Account (الحساب)

يمثل حساباً محاسبياً في نظام الدفتر الكبير.

```python
account = Account(
    name="Cash Account",
    account_type="asset",
    code="1000-CASH",
    currency="USD",
    description="Company cash account"
)

# إضافة مبلغ
account.deposit(1000, "Initial cash")

# سحب مبلغ
account.withdraw(500, "Cash expense")

# الحصول على الرصيد
balance = account.get_balance()
```

**أنواع الحسابات:**
- `asset` - الأصول (الأموال، المستثمرات، الممتلكات)
- `liability` - الالتزامات (القروض، الحسابات الدائنة)
- `equity` - حقوق الملكية (رأس المال)
- `income` - الإيرادات (المبيعات، الفوائد)
- `expense` - المصروفات (الرواتب، الإيجار)

#### 2. Ledger (دفتر الحسابات)

يجمع الحسابات المختلفة ويدير المعاملات.

```python
ledger = Ledger("Main Ledger", currency="USD")

# إضافة حساب
ledger.add_account(account)

# الحصول على حساب
cash_account = ledger.get_account("1000-CASH")

# تحويل بين حسابين
ledger.transfer(from_account=cash, to_account=expense, amount=500)

# الحصول على ميزان المراجعة
trial_balance = ledger.get_trial_balance()
```

#### 3. JournalEntry (القيد اليومي)

تسجيل معاملة محاسبية متوازنة.

```python
entry = JournalEntry("Daily transaction", description="Sales transaction")

# إضافة طرف مدين
entry.add_debit(cash, 1000, "Cash received")

# إضافة طرف دائن
entry.add_credit(sales, 1000, "Revenue recognized")

# التحقق من التوازن
if entry.is_balanced():
    entry.post()
```

#### 4. Invoice (الفاتورة)

إدارة الفواتير والمدفوعات.

```python
invoice = Invoice("Customer Name")

# إضافة بنود
invoice.add_item("Product 1", quantity=2, unit_price=100)
invoice.add_item("Service", quantity=1, unit_price=50)

# حساب الإجمالي
total = invoice.calculate_total()

# تسجيل الدفع
invoice.pay(amount=250, method='cash')

# التحقق من الحالة
print(invoice.get_status())  # 'paid'
```

#### 5. Tax (الضريبة)

حساب الضرائب المختلفة.

```python
# إنشاء ضريبة
vat = Tax("VAT", rate=15)

# حساب مبلغ الضريبة
tax_amount = vat.calculate(1000)  # 150

# حساب الإجمالي مع الضريبة
total_with_tax = vat.calculate_total(1000)  # 1150
```

#### 6. Payment (الدفع)

إدارة المدفوعات.

```python
payment = Payment(amount=500, method='bank_transfer')
payment.process()

# التحقق من حالة الدفع
print(payment.get_status())  # 'completed'
```

#### 7. Reports (التقارير)

إنشاء التقارير المالية.

```python
# قائمة الدخل
income_stmt = IncomeStatement(ledger)
income_data = income_stmt.generate()

# الميزانية العمومية
balance_sheet = BalanceSheet(ledger)
balance_data = balance_sheet.generate()

# بيان التدفقات النقدية
cash_flow = CashFlowStatement(ledger)
cash_flow_data = cash_flow.generate()
```

## 💱 دعم العملات

```python
from pyledger import CurrencyConverter

converter = CurrencyConverter()

# تحويل من USD إلى EUR
amount_eur = converter.convert(100, 'USD', 'EUR')
```

## 🔒 معالجة الأخطاء

```python
from pyledger import *

try:
    account = ledger.get_account("NONEXISTENT")
except AccountNotFoundError as e:
    print(f"Error: {e}")

try:
    account.withdraw(10000)
except InsufficientBalanceError as e:
    print(f"Error: {e}")

try:
    entry = JournalEntry("Unbalanced")
    entry.add_debit(cash, 100)
    entry.add_credit(sales, 50)  # غير متساوي!
    entry.post()
except UnbalancedEntryError as e:
    print(f"Error: {e}")
```

## 📄 الترخيص

هذا المشروع مرخص تحت رخصة Apache 2.0 - انظر ملفي LICENSE و NOTICE للتفاصيل.
الاستخدام التجاري مسموح بالكامل، مع وجوب الاحتفاظ بإشعار النسبة إلى PyLedger عند التوزيع.

## 🤝 المساهمة

نرحب بالمساهمات! يرجى قراءة [CONTRIBUTING.md](CONTRIBUTING.md) ثم عمل Fork للمشروع وإرسال Pull Request.

---

**صنع بـ ❤️ من قبل فريق PyLedger**
