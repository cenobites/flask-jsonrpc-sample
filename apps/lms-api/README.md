# Flask-JSONRPC-sample

Sample project for a library management system (LMS) using Flask-JSONRPC.

---

## Models

* Branch - Library branch with staff and manager
* Patron - Library members with status tracking
* Staff - Employees with roles and branch assignment
* Publisher - Publishers for items and serials
* Category - Categories for classification
* Author - Authors linked via many-to-many to items
* Item - Bibliographic records (books, DVDs, etc.)
* Copy - Physical copies of items
* Loan - Circulation transactions
* Hold - Reservations
* Vendor - Vendors for acquisitions
* AcquisitionOrder - Purchase orders
* AcquisitionOrderLine - Order line items
* Serial - Serial publications/subscriptions
* SerialIssue - Individual serial issues
* Fine - Patron fines
* Report - Statistics and reportsl

## Relations

## 📘 Library Management System – Data Entity Relationship (DER)

### **1. Branch**

* **Fields:**

  * `id` (PK)
  * `name`
  * `address`
  * `phone`
  * `manager_id` → FK → `Staff.id`
* **Relationships:**

  * Has many **Staff**
  * Has many **Patrons**
  * Has many **Loans**
  * Has many **Items (Copies located here)**

---

### **2. Staff**

* **Fields:**

  * `id` (PK)
  * `first_name`
  * `last_name`
  * `role` (e.g. Librarian, Clerk, Manager)
  * `branch_id` → FK → `Branch.id`
* **Relationships:**

  * Belongs to one **Branch**
  * Can manage one **Branch** (if `role='Manager'`)
  * Can process many **Loans** or **AcquisitionOrders**

---

### **3. Patron**

* **Fields:**

  * `id` (PK)
  * `first_name`
  * `last_name`
  * `email`
  * `status` (Active, Suspended, etc.)
  * `branch_id` → FK → `Branch.id`
* **Relationships:**

  * Belongs to one **Branch**
  * Has many **Loans**
  * Has many **Holds**
  * Can have many **Fines**

---

### **4. Category**

* **Fields:**

  * `id` (PK)
  * `name`
  * `description`
* **Relationships:**

  * Has many **Items**

---

### **5. Publisher**

* **Fields:**

  * `id` (PK)
  * `name`
  * `address`
  * `contact_info`
* **Relationships:**

  * Publishes many **Items**
  * Linked to **Serials**

---

### **6. Author**

* **Fields:**

  * `id` (PK)
  * `first_name`
  * `last_name`
* **Relationships:**

  * Many-to-many with **Item** through a join table `item_authors`

---

### **7. Item**

* **Fields:**

  * `id` (PK)
  * `title`
  * `isbn`
  * `publication_date`
  * `publisher_id` → FK → `Publisher.id`
  * `category_id` → FK → `Category.id`
  * `item_type` (Book, DVD, etc.)
* **Relationships:**

  * Many-to-many with **Author**
  * Has many **Copies**
  * May have many **SerialIssues** (if it’s a serial)

---

### **8. Copy**

* **Fields:**

  * `id` (PK)
  * `item_id` → FK → `Item.id`
  * `branch_id` → FK → `Branch.id`
  * `barcode`
  * `status` (Available, On Loan, Lost, etc.)
* **Relationships:**

  * Belongs to one **Item**
  * Belongs to one **Branch**
  * Can be linked to **Loans** and **Holds**

---

### **9. Loan**

* **Fields:**

  * `id` (PK)
  * `copy_id` → FK → `Copy.id`
  * `patron_id` → FK → `Patron.id`
  * `staff_id` → FK → `Staff.id` (who issued it)
  * `loan_date`
  * `due_date`
  * `return_date`
* **Relationships:**

  * Belongs to one **Copy**
  * Belongs to one **Patron**
  * Processed by one **Staff**
  * May generate a **Fine**

---

### **10. Hold**

* **Fields:**

  * `id` (PK)
  * `patron_id` → FK → `Patron.id`
  * `copy_id` → FK → `Copy.id` (or `item_id` if on the title)
  * `request_date`
  * `status` (Pending, Ready, Fulfilled)
* **Relationships:**

  * Belongs to one **Patron**
  * Refers to one **Copy** (or **Item**)

---

### **11. Vendor**

* **Fields:**

  * `id` (PK)
  * `name`
  * `contact_info`
  * `address`
* **Relationships:**

  * Supplies many **AcquisitionOrders**

---

### **12. AcquisitionOrder**

* **Fields:**

  * `id` (PK)
  * `vendor_id` → FK → `Vendor.id`
  * `staff_id` → FK → `Staff.id`
  * `order_date`
  * `status`
* **Relationships:**

  * Has many **AcquisitionOrderLines**
  * Belongs to one **Vendor**
  * Created by one **Staff**

---

### **13. AcquisitionOrderLine**

* **Fields:**

  * `id` (PK)
  * `order_id` → FK → `AcquisitionOrder.id`
  * `item_id` → FK → `Item.id`
  * `quantity`
  * `unit_price`
* **Relationships:**

  * Belongs to one **AcquisitionOrder**
  * Refers to one **Item**

---

### **14. Serial**

* **Fields:**

  * `id` (PK)
  * `title`
  * `publisher_id` → FK → `Publisher.id`
  * `issn`
  * `frequency`
* **Relationships:**

  * Has many **SerialIssues**

---

### **15. SerialIssue**

* **Fields:**

  * `id` (PK)
  * `serial_id` → FK → `Serial.id`
  * `issue_number`
  * `publication_date`
* **Relationships:**

  * Belongs to one **Serial**

---

### **16. Fine**

* **Fields:**

  * `id` (PK)
  * `patron_id` → FK → `Patron.id`
  * `loan_id` → FK → `Loan.id`
  * `amount`
  * `status` (Unpaid, Paid)
* **Relationships:**

  * Belongs to one **Patron**
  * Related to one **Loan**

---

### **17. Report**

* **Fields:**

  * `id` (PK)
  * `title`
  * `report_type`
  * `generated_at`
  * `data` (JSON or file link)
* **Relationships:**

  * May aggregate data from **Loans**, **Fines**, **Acquisitions**, etc.

---

## 🔗 High-Level Relationship Summary

| Relationship                            | Type         |
| --------------------------------------- | ------------ |
| Branch — Staff                          | 1-to-many    |
| Branch — Patron                         | 1-to-many    |
| Branch — Copy                           | 1-to-many    |
| Staff — Loan                            | 1-to-many    |
| Patron — Loan                           | 1-to-many    |
| Patron — Hold                           | 1-to-many    |
| Patron — Fine                           | 1-to-many    |
| Item — Copy                             | 1-to-many    |
| Item — Author                           | many-to-many |
| Item — Category                         | many-to-1    |
| Item — Publisher                        | many-to-1    |
| Copy — Loan                             | 1-to-many    |
| Vendor — AcquisitionOrder               | 1-to-many    |
| AcquisitionOrder — AcquisitionOrderLine | 1-to-many    |
| Serial — SerialIssue                    | 1-to-many    |

---


---

## 🧩 JSON-RPC Base

Below is a complete **JSON-RPC method schema** derived from your LMS REST API.

```
POST /api/v1/jsonrpc
Content-Type: application/json
Authorization: Bearer <token>
```

---

## 🧱 1. Authentication & User Management

| REST                  | JSON-RPC Method  | Params                          |
| :-------------------- | :--------------- | :------------------------------ |
| `POST /auth/login`    | `auth.login`     | `{username, password}`          |
| `POST /auth/logout`   | `auth.logout`    | `{}`                            |
| `POST /auth/register` | `auth.register`  | `{name, email, password, role}` |
| `GET /auth/me`        | `auth.me.get`    | `{}`                            |
| `PATCH /auth/me`      | `auth.me.update` | `{name?, email?, password?}`    |
| `POST /auth/refresh`  | `auth.refresh`   | `{refresh_token}`               |

---

## 👤 2. Patrons

| REST                      | JSON-RPC Method | Params                                   |
| :------------------------ | :-------------- | :--------------------------------------- |
| `GET /patrons`            | `patron.list`   | `{page?, filter?}`                       |
| `POST /patrons`           | `patron.create` | `{name, email, address, status}`         |
| `GET /patrons/{id}`       | `patron.get`    | `{id}`                                   |
| `PATCH /patrons/{id}`     | `patron.update` | `{id, name?, email?, address?, status?}` |
| `DELETE /patrons/{id}`    | `patron.delete` | `{id}`                                   |
| `GET /patrons/{id}/loans` | `patron.loans`  | `{id}`                                   |
| `GET /patrons/{id}/holds` | `patron.holds`  | `{id}`                                   |
| `GET /patrons/{id}/fines` | `patron.fines`  | `{id}`                                   |

---

## 📚 3. Cataloging

| REST                              | JSON-RPC Method       | Params                             |
| :-------------------------------- | :-------------------- | :--------------------------------- |
| `GET /catalog/items`              | `catalog.list`        | `{query?, filters?}`               |
| `POST /catalog/items`             | `catalog.create`      | `{title, author, isbn, category}`  |
| `GET /catalog/items/{id}`         | `catalog.get`         | `{id}`                             |
| `PATCH /catalog/items/{id}`       | `catalog.update`      | `{id, title?, author?, metadata?}` |
| `DELETE /catalog/items/{id}`      | `catalog.delete`      | `{id}`                             |
| `GET /catalog/items/{id}/copies`  | `catalog.copies`      | `{id}`                             |
| `POST /catalog/items/{id}/copies` | `catalog.copy.create` | `{item_id, barcode, branch_id}`    |

---

## 🏷️ 4. Copies / Holdings

| REST                           | JSON-RPC Method    | Params                      |
| :----------------------------- | :----------------- | :-------------------------- |
| `GET /copies`                  | `copy.list`        | `{}`                        |
| `GET /copies/{id}`             | `copy.get`         | `{id}`                      |
| `PATCH /copies/{id}`           | `copy.update`      | `{id, status?, condition?}` |
| `DELETE /copies/{id}`          | `copy.delete`      | `{id}`                      |
| `GET /copies/{id}/circulation` | `copy.circulation` | `{id}`                      |

---

## 🔁 5. Circulation

| REST                                   | JSON-RPC Method | Params                                |
| :------------------------------------- | :-------------- | :------------------------------------ |
| `GET /circulation/loans`               | `loan.list`     | `{}`                                  |
| `POST /circulation/loans`              | `loan.create`   | `{patron_id, copy_id, due_date}`      |
| `GET /circulation/loans/{id}`          | `loan.get`      | `{id}`                                |
| `PATCH /circulation/loans/{id}/renew`  | `loan.renew`    | `{id}`                                |
| `PATCH /circulation/loans/{id}/return` | `loan.return`   | `{id}`                                |
| `GET /circulation/history`             | `loan.history`  | `{patron_id?, item_id?, date_range?}` |

---

## 📅 6. Holds / Reservations

| REST                        | JSON-RPC Method | Params                 |
| :-------------------------- | :-------------- | :--------------------- |
| `GET /holds`                | `hold.list`     | `{}`                   |
| `POST /holds`               | `hold.create`   | `{patron_id, item_id}` |
| `GET /holds/{id}`           | `hold.get`      | `{id}`                 |
| `PATCH /holds/{id}/cancel`  | `hold.cancel`   | `{id}`                 |
| `PATCH /holds/{id}/fulfill` | `hold.fulfill`  | `{id}`                 |

---

## 💰 7. Fines & Payments

| REST                    | JSON-RPC Method | Params                        |
| :---------------------- | :-------------- | :---------------------------- |
| `GET /fines`            | `fine.list`     | `{}`                          |
| `POST /fines`           | `fine.create`   | `{patron_id, amount, reason}` |
| `GET /fines/{id}`       | `fine.get`      | `{id}`                        |
| `PATCH /fines/{id}/pay` | `fine.pay`      | `{id, payment_method}`        |
| `DELETE /fines/{id}`    | `fine.delete`   | `{id}`                        |

---

## 🏛️ 8. Branches & Staff

| REST                           | JSON-RPC Method    | Params                   |
| :----------------------------- | :----------------- | :----------------------- |
| `GET /branches`                | `branch.list`      | `{}`                     |
| `POST /branches`               | `branch.create`    | `{name, location}`       |
| `GET /branches/{id}`           | `branch.get`       | `{id}`                   |
| `PATCH /branches/{id}`         | `branch.update`    | `{id, name?, location?}` |
| `DELETE /branches/{id}`        | `branch.delete`    | `{id}`                   |
| `GET /branches/{id}/inventory` | `branch.inventory` | `{id}`                   |
| `GET /staff`                   | `staff.list`       | `{}`                     |
| `POST /staff`                  | `staff.create`     | `{name, role, email}`    |

---

## 🛒 9. Acquisitions

| REST                               | JSON-RPC Method            | Params                           |
| :--------------------------------- | :------------------------- | :------------------------------- |
| `GET /acquisitions/orders`         | `acquisition.order.list`   | `{}`                             |
| `POST /acquisitions/orders`        | `acquisition.order.create` | `{vendor_id, items, total_cost}` |
| `GET /acquisitions/orders/{id}`    | `acquisition.order.get`    | `{id}`                           |
| `PATCH /acquisitions/orders/{id}`  | `acquisition.order.update` | `{id, status}`                   |
| `DELETE /acquisitions/orders/{id}` | `acquisition.order.delete` | `{id}`                           |
| `GET /vendors`                     | `vendor.list`              | `{}`                             |
| `POST /vendors`                    | `vendor.create`            | `{name, contact_info}`           |

---

## 📰 10. Serials & Subscriptions

| REST                        | JSON-RPC Method       | Params                                     |
| :-------------------------- | :-------------------- | :----------------------------------------- |
| `GET /serials`              | `serial.list`         | `{}`                                       |
| `POST /serials`             | `serial.create`       | `{title, issn, publisher}`                 |
| `GET /serials/{id}`         | `serial.get`          | `{id}`                                     |
| `PATCH /serials/{id}`       | `serial.update`       | `{id, title?, publisher?}`                 |
| `GET /serials/{id}/issues`  | `serial.issue.list`   | `{serial_id}`                              |
| `POST /serials/{id}/issues` | `serial.issue.create` | `{serial_id, issue_number, date_received}` |

---

## 🧾 11. Reports & Analytics

| REST                           | JSON-RPC Method          | Params                  |
| :----------------------------- | :----------------------- | :---------------------- |
| `GET /reports/loans`           | `report.loans`           | `{range?, group_by?}`   |
| `GET /reports/fines`           | `report.fines`           | `{range?}`              |
| `GET /reports/inventory`       | `report.inventory`       | `{branch_id?, status?}` |
| `GET /reports/patron-activity` | `report.patron_activity` | `{patron_id?, range?}`  |

---

## ⚙️ 12. System / Configuration

| REST                     | JSON-RPC Method          | Params                           |
| :----------------------- | :----------------------- | :------------------------------- |
| `GET /config/settings`   | `config.settings.get`    | `{}`                             |
| `PATCH /config/settings` | `config.settings.update` | `{loan_limit?, fine_rate?}`      |
| `GET /config/policies`   | `config.policies.get`    | `{}`                             |
| `PATCH /config/policies` | `config.policies.update` | `{loan_duration?, fine_policy?}` |
| `GET /health`            | `system.health`          | `{}`                             |

---

## 🔒 Optional Modules

| Module            | JSON-RPC Methods                         |
| :---------------- | :--------------------------------------- |
| **Notifications** | `notification.list`, `notification.send` |
| **Digital Media** | `ebook.list`, `ebook.download`           |
| **OPAC**          | `opac.search`, `opac.get_item`           |

---
