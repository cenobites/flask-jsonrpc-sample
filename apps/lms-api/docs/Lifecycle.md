## 🏛️ 1. **Branch**

### 📈 Lifecycle

* **Created** when a new library branch is established.
* **Active** while it serves patrons and manages inventory.
* **Archived/closed** when merged or shut down.

### ⚙️ Core Business State

* `id`, `name`, `address`, `phone`, `manager_id`.

### 🧠 Domain Behaviors

* Assign a manager or reassign staff.
* Manage branch-specific holdings (copies).
* Track open hours or operational status.

---

## 👤 2. **Patron**

### 📈 Lifecycle

* **Registered** when they join the library.
* **Active** while membership is valid.
* **Suspended** when overdue or fines unpaid.
* **Archived** after membership expiration or deletion.

### ⚙️ Core Business State

* `id`, `name`, `email`, `status`, `fines_due`, `active_loans`.

### 🧠 Domain Behaviors

* Register / activate / suspend / deactivate.
* Borrow and return items (through loans).
* Place and cancel holds.
* Pay fines or check loan eligibility.

---

## 👔 3. **Staff**

### 📈 Lifecycle

* **Created** when hired.
* **Active** when assigned to a branch.
* **Inactive** when terminated or transferred.

### ⚙️ Core Business State

* `id`, `name`, `role` (librarian, assistant), `branch_id`.

### 🧠 Domain Behaviors

* Manage loans, holds, and acquisitions.
* Approve patron registrations.
* Create or process acquisition orders.

---

## 🏢 4. **Publisher**

### 📈 Lifecycle

* **Created** when first referenced in cataloging or acquisitions.
* **Updated** as contact info changes.
* **Inactive** when defunct or no longer publishing.

### ⚙️ Core Business State

* `id`, `name`, `address`, `contact_info`.

### 🧠 Domain Behaviors

* Update contact information.
* Link to items and serials published by it.

---

## 🏷️ 5. **Category**

### 📈 Lifecycle

* **Created** when classification schema is established.
* **Updated** as taxonomy evolves.
* **Archived** when replaced or deprecated.

### ⚙️ Core Business State

* `id`, `name`, `description`.

### 🧠 Domain Behaviors

* Classify or reclassify items.
* Support hierarchical or keyword search.

---

## ✍️ 6. **Author**

### 📈 Lifecycle

* **Created** when cataloging an authored work.
* **Updated** with metadata or pseudonyms.
* **Archived** rarely; usually permanent.

### ⚙️ Core Business State

* `id`, `first_name`, `last_name`.

### 🧠 Domain Behaviors

* Link to items via many-to-many relationships.
* Merge duplicate author records.
* Retrieve all works by author.

---

## 📚 7. **Item**

### 📈 Lifecycle

* **Created** when cataloged for the first time.
* **Active** while copies are available.
* **Withdrawn** when all copies are removed.

### ⚙️ Core Business State

* `id`, `title`, `isbn`, `publisher_id`, `category_id`, `authors`.

### 🧠 Domain Behaviors

* Link to authors, category, publisher.
* Manage metadata updates (title, edition, etc.).
* Determine if serial or monograph.
* Manage related copies.

---

## 🧾 8. **Copy**

### 📈 Lifecycle

* **Created** when a physical copy is acquired or cataloged.
* **On shelf** (available) → **On loan** → **Returned** → possibly **Lost/Damaged/Withdrawn**.

### ⚙️ Core Business State

* `id`, `barcode`, `status`, `item_id`, `branch_id`.

### 🧠 Domain Behaviors

* Change status (`available`, `on_loan`, `lost`).
* Track physical location and circulation history.
* Mark as withdrawn or repaired.

---

## 🔁 9. **Loan**

### 📈 Lifecycle

* **Created** when a patron borrows a copy.
* **Active** until returned.
* **Closed** when returned or renewed.
* **May lead to fine** if overdue.

### ⚙️ Core Business State

* `id`, `patron_id`, `copy_id`, `loan_date`, `due_date`, `return_date`.

### 🧠 Domain Behaviors

* Renew or close loan.
* Determine overdue status.
* Calculate fine based on days overdue.
* Trigger fine creation event.

---

## 📅 10. **Hold**

### 📈 Lifecycle

* **Placed** when a patron reserves a copy/item.
* **Pending** until available.
* **Ready** when the item is available.
* **Fulfilled** when loaned.
* **Cancelled/Expired** when no longer needed.

### ⚙️ Core Business State

* `id`, `patron_id`, `copy_id`, `status`, `request_date`.

### 🧠 Domain Behaviors

* Place or cancel hold.
* Fulfill hold when copy becomes available.
* Notify patron of availability.

---

## 🏪 11. **Vendor**

### 📈 Lifecycle

* **Created** when first used for acquisitions.
* **Active** while supplying materials.
* **Inactive** when no longer in business.

### ⚙️ Core Business State

* `id`, `name`, `address`, `contact_info`.

### 🧠 Domain Behaviors

* Manage vendor information.
* Associate acquisition orders.

---

## 📦 12. **AcquisitionOrder**

### 📈 Lifecycle

* **Created** when a purchase request is approved.
* **Submitted** to vendor.
* **Received** when items arrive.
* **Closed** when all lines fulfilled.

### ⚙️ Core Business State

* `id`, `vendor_id`, `staff_id`, `status`, `order_date`, `total_amount`.

### 🧠 Domain Behaviors

* Add or remove line items.
* Submit order to vendor.
* Receive and reconcile items.
* Calculate total cost.
* Mark order as closed.

---

## 📄 13. **AcquisitionOrderLine**

### 📈 Lifecycle

* **Created** when added to an order.
* **Active** until fulfilled.
* **Closed** when received.

### ⚙️ Core Business State

* `id`, `order_id`, `item_id`, `quantity`, `unit_price`.

### 🧠 Domain Behaviors

* Update quantity or price.
* Mark as received.
* Calculate line total.

---

## 🗞️ 14. **Serial**

### 📈 Lifecycle

* **Created** when subscription starts.
* **Active** while issues are being published.
* **Inactive** when canceled.

### ⚙️ Core Business State

* `id`, `title`, `issn`, `publisher_id`, `frequency`.

### 🧠 Domain Behaviors

* Add new issues.
* Manage subscription status.
* Track renewal date.
* Link to publisher and items.

---

## 📰 15. **SerialIssue**

### 📈 Lifecycle

* **Created** for each new issue.
* **Received** when it arrives at branch.
* **Cataloged** as an `Item`.
* **Archived/Withdrawn** when out of circulation.

### ⚙️ Core Business State

* `id`, `serial_id`, `issue_number`, `volume_number`, `publication_date`, `status`.

### 🧠 Domain Behaviors

* Register new issue arrival.
* Link to bibliographic item.
* Update availability or archival status.

---

## 💰 16. **Fine**

### 📈 Lifecycle

* **Created** automatically when a loan is overdue.
* **Active** until paid or waived.
* **Closed** after payment or cancellation.

### ⚙️ Core Business State

* `id`, `patron_id`, `loan_id`, `amount`, `status`.

### 🧠 Domain Behaviors

* Calculate fine based on overdue duration.
* Apply payment or waiver.
* Trigger patron suspension if unpaid.

---

## 🧠 Summary Table

| Entity                   | Lifecycle                                      | Core State                | Core Behavior           |
| ------------------------ | ---------------------------------------------- | ------------------------- | ----------------------- |
| **Branch**               | Created → Active → Closed                      | id, name, manager         | Manage staff, holdings  |
| **Patron**               | Registered → Active → Suspended → Archived     | id, name, status          | Borrow, hold, pay fines |
| **Staff**                | Hired → Active → Inactive                      | id, name, role            | Manage operations       |
| **Publisher**            | Created → Active → Inactive                    | name, contact             | Publish items/serials   |
| **Category**             | Created → Active → Archived                    | name, description         | Classify items          |
| **Author**               | Created → Active                               | name                      | Link to items           |
| **Item**                 | Cataloged → Active → Withdrawn                 | title, publisher, authors | Manage metadata, copies |
| **Copy**                 | Created → On shelf → On loan → Returned → Lost | barcode, status           | Change status           |
| **Loan**                 | Created → Active → Closed                      | due_date, return_date     | Renew, close, fine      |
| **Hold**                 | Placed → Ready → Fulfilled/Cancelled           | status, request_date      | Reserve, fulfill        |
| **Vendor**               | Created → Active → Inactive                    | name, contact             | Supply orders           |
| **AcquisitionOrder**     | Created → Submitted → Received → Closed        | vendor_id, status         | Manage order flow       |
| **AcquisitionOrderLine** | Added → Fulfilled → Closed                     | quantity, price           | Track receipt           |
| **Serial**               | Created → Active → Inactive                    | title, frequency          | Manage subscription     |
| **SerialIssue**          | Created → Received → Archived                  | issue_number, status      | Register issue          |
| **Fine**                 | Created → Active → Closed                      | amount, status            | Apply payment or waive  |

---
