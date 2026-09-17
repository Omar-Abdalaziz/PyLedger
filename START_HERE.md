# 🚀 PyLedger - ابدأ الآن!

## ⚡ البدء في 30 ثانية

```python
from pyledger import Ledger, Account, JournalEntry

# إنشاء دفتر
ledger = Ledger("شركتي")

# إنشاء حسابات
cash = Account("النقدية", "asset", "1000")
sales = Account("المبيعات", "income", "4000")

# إضافتها
ledger.add_account(cash)
ledger.add_account(sales)

# معاملة
entry = JournalEntry("مبيعات")
entry.add_debit(cash, 1000)
entry.add_credit(sales, 1000)
entry.post()

ledger.record_entry(entry)
```

**هذا كل شيء!** ✅

---

## 📂 الملفات المهمة

| الملف | قراءة في | للـ |
|------|---------|-----|
| **SUCCESS.md** | 2 دقيقة | ملخص الإنجاز |
| **README.md** | 10 دقائق | التوثيق |
| **QUICKSTART.md** | 5 دقائق | البدء السريع |
| **example.py** | يعمل مباشرة | مثال فوري |
| **INDEX.md** | 5 دقائق | الفهرس |

---

## 🎯 خطوة واحدة فقط:

### اختر مسارك:

**① أنا مشغول - أريد مثال سريع**
```bash
python example.py
```

**② أنا جديد - أريد توثيق**
```markdown
اقرأ: README.md
```

**③ أنا محترف - أريد أمثلة متقدمة**
```markdown
اقرأ: EXAMPLES.md
```

---

## ✨ ماذا يمكنك فعله؟

- ✅ إنشاء نظام محاسبة كامل
- ✅ إدارة الفواتير والدفعات
- ✅ حساب الضرائب المختلفة
- ✅ العمل مع عملات متعددة
- ✅ إنشاء تقارير مالية
- ✅ تخزين البيانات في قاعدة بيانات

---

## 📖 المراجع السريعة

### الحسابات
```python
from pyledger import Account

# إنشاء
account = Account("اسم", "asset", "1000")

# عمليات
account.deposit(1000)
account.withdraw(500)
balance = account.get_balance()
```

### الفواتير
```python
from pyledger import Invoice, Tax

invoice = Invoice("عميل")
invoice.add_item("منتج", 1, 100)
invoice.add_tax(Tax("VAT", 15))
invoice.pay(120)
```

### التقارير
```python
from pyledger import IncomeStatement, BalanceSheet

stmt = IncomeStatement(ledger)
bs = BalanceSheet(ledger)

print(stmt)
print(bs)
```

---

## 🎓 رابط التعلم

```
البدء
  ↓
SUCCESS.md (2 دقيقة) - اقرأ الملخص
  ↓
example.py (2 دقيقة) - شغّل المثال
  ↓
QUICKSTART.md (5 دقائق) - تعلم الأساسيات
  ↓
README.md (15 دقيقة) - اقرأ التوثيق
  ↓
EXAMPLES.md (30 دقيقة) - استكشف الأمثلة
  ↓
pyledger/ (1 ساعة) - ادرس الكود
  ↓
ابنِ مشروعك! 🚀
```

---

## 🤔 لماذا PyLedger؟

| الميزة | الفائدة |
|--------|---------|
| **محترفة** | معايير محاسبية حقيقية |
| **آمنة** | معالجة آمنة للبيانات المالية |
| **موثقة** | أكثر من 2000 سطر توثيق |
| **مختبرة** | 40+ حالة اختبار |
| **سهلة** | API بسيطة وواضحة |
| **مرنة** | قابلة للتوسع بسهولة |

---

## ⏱️ الوقت المتوقع

- **البدء الأول:** 5 دقائق
- **فهم الأساسيات:** 15 دقيقة
- **بناء تطبيق بسيط:** 30 دقيقة
- **إتقان المكتبة:** 2-3 ساعات

---

## 🎉 جاهز؟

### خيارك الأول: اقرأ الملخص
→ **[اقرأ SUCCESS.md](SUCCESS.md)** (2 دقيقة)

### خيارك الثاني: شغّل مثال
→ **`python example.py`** (فوري!)

### خيارك الثالث: اقرأ التوثيق
→ **[اقرأ README.md](README.md)** (شامل)

---

## 💡 نصيحة

> "أفضل طريقة للتعلم هي العملية!"
> 
> شغّل `example.py` الآن، وستفهم كل شيء! 🚀

---

**آخر تحديث:** 14 مارس 2026  
**الإصدار:** 1.0.0

**ابدأ الآن!** 🎉
