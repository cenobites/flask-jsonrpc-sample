## 🧩 1. What’s an Aggregate and an Aggregate Root?

In DDD terms:

| Concept                | Meaning                                                                                                             |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------- |
| **Aggregate**          | A **cluster of domain objects** (entities + value objects) that should be treated as a **single consistency unit**. |
| **Aggregate Root**     | The **entry point** to that cluster — the only entity you load/save via a repository.                               |
| **Invariant Boundary** | All business rules that must be consistent are enforced **inside the aggregate boundary**.                          |

👉 So: you never modify child entities directly from outside; you always go through the aggregate root.

---

## 🧱 2. Applying This to the Library Domain

Let’s group the entities by domain area and identify which are **aggregates** and which are **children** (or referenced externally).

---

### 📚 **Catalog & Collection Management**

| Entity          | Aggregate Root?     | Reason / Ownership                                                            |
| --------------- | ------------------- | ----------------------------------------------------------------------------- |
| **Category**    | ✅ Yes               | Independent taxonomy; rarely changes, no parent.                              |
| **Publisher**   | ✅ Yes               | Managed independently; referenced by items.                                   |
| **Author**      | ✅ Yes               | Independent identity, referenced by items.                                    |
| **Item**        | ✅ Yes               | Core bibliographic entity; owns **Copies**.                                   |
| **Copy**        | ❌ Child of `Item`   | Its lifecycle (available, lost, withdrawn) depends on the item it belongs to. |
| **Serial**      | ✅ Yes               | Represents ongoing subscription; owns **SerialIssues**.                       |
| **SerialIssue** | ❌ Child of `Serial` | Always belongs to a parent serial. Cannot exist on its own.                   |

**Aggregate boundaries here:**

* `Item` aggregate: Item → Copies
* `Serial` aggregate: Serial → SerialIssues

---

### 🧾 **Circulation**

| Entity     | Aggregate Root? | Reason / Ownership                                                                         |
| ---------- | --------------- | ------------------------------------------------------------------------------------------ |
| **Patron** | ✅ Yes           | Central actor in circulation; owns membership state, fines, holds, and loan relationships. |
| **Loan**   | ✅ Yes           | Represents a transactional record; needs independent persistence and lifecycle.            |
| **Hold**   | ✅ Yes           | Represents a queue request; interacts with Patron and Copy but has its own state.          |
| **Fine**   | ✅ Yes           | Result of a domain event (e.g., overdue loan); managed and paid separately.                |

**Aggregate boundaries:**

* `Patron` aggregate: may reference loans/holds/fines but not own them (loose coupling, as those are transactional).
* `Loan`, `Hold`, and `Fine` are separate aggregates linked via IDs.

---

### 🏢 **Organization**

| Entity     | Aggregate Root? | Reason / Ownership                                        |
| ---------- | --------------- | --------------------------------------------------------- |
| **Branch** | ✅ Yes           | Defines staff and copies location; independent lifecycle. |
| **Staff**  | ✅ Yes           | Independent identity, can move between branches.          |

**Aggregate boundaries:**

* `Branch` may *reference* staff but not own their lifecycle (staff are independent).

---

### 💼 **Acquisitions**

| Entity                   | Aggregate Root?               | Reason / Ownership                          |
| ------------------------ | ----------------------------- | ------------------------------------------- |
| **Vendor**               | ✅ Yes                         | Independent identity; referenced by orders. |
| **AcquisitionOrder**     | ✅ Yes                         | Transaction root for ordering process.      |
| **AcquisitionOrderLine** | ❌ Child of `AcquisitionOrder` | Always belongs to one order.                |

**Aggregate boundaries:**

* `AcquisitionOrder` aggregate: AcquisitionOrder → AcquisitionOrderLines

---

## 🧩 3. Relationships and Ownership Summary

| Aggregate Root       | Owned Entities        | References To                 |
| -------------------- | --------------------- | ----------------------------- |
| **Branch**           | —                     | Staff, Copies                 |
| **Staff**            | —                     | Branch                        |
| **Patron**           | —                     | Loans, Holds, Fines (via IDs) |
| **Item**             | Copies                | Authors, Publisher, Category  |
| **Serial**           | SerialIssues          | Publisher                     |
| **Loan**             | —                     | Patron, Copy                  |
| **Hold**             | —                     | Patron, Copy                  |
| **Fine**             | —                     | Patron, Loan                  |
| **Vendor**           | —                     | AcquisitionOrders             |
| **AcquisitionOrder** | AcquisitionOrderLines | Vendor, Staff                 |

---

## 🧠 4. Repository Design Guidelines

Each **Aggregate Root** gets its own repository.

| Aggregate Root                    | Repository Example                     |
| --------------------------------- | -------------------------------------- |
| `Patron`                          | `PatronRepository`                     |
| `Branch`                          | `BranchRepository`                     |
| `Staff`                           | `StaffRepository`                      |
| `Item`                            | `ItemRepository`                       |
| `Serial`                          | `SerialRepository`                     |
| `Loan`                            | `LoanRepository`                       |
| `Hold`                            | `HoldRepository`                       |
| `Fine`                            | `FineRepository`                       |
| `Vendor`                          | `VendorRepository`                     |
| `AcquisitionOrder`                | `AcquisitionOrderRepository`           |
| `Category`, `Publisher`, `Author` | Optional (reference data repositories) |

These repositories are the only way to **retrieve and persist aggregates**.

---

## 🧩 5. Consistency Rules (Invariants) Per Aggregate

| Aggregate Root       | Must Ensure That…                                                                    |
| -------------------- | ------------------------------------------------------------------------------------ |
| **Patron**           | Email is unique; status is valid; cannot borrow if suspended.                        |
| **Item**             | Copies belong to this item only; metadata consistent across copies.                  |
| **Serial**           | Issue numbering is sequential; publication frequency respected.                      |
| **Loan**             | Copy and Patron exist; due date valid; cannot duplicate active loan for same copy.   |
| **Hold**             | Only one active hold per patron per item; state transitions valid.                   |
| **Fine**             | Tied to exactly one loan; cannot be paid twice.                                      |
| **AcquisitionOrder** | All line totals sum to total; only valid items can be ordered; cannot receive twice. |

---

## 🧠 6. Simplified Aggregate Structure Overview

```plaintext
Branch (Root)
 ├── references → Staff, Copies

Staff (Root)
 └── references → Branch

Patron (Root)
 ├── references → Loan IDs, Hold IDs, Fine IDs

Item (Root)
 ├── owns → Copies
 ├── references → Authors, Category, Publisher

Serial (Root)
 ├── owns → SerialIssues

Loan (Root)
 ├── references → Patron, Copy

Hold (Root)
 ├── references → Patron, Copy

Fine (Root)
 ├── references → Patron, Loan

Vendor (Root)
 ├── references → AcquisitionOrders

AcquisitionOrder (Root)
 ├── owns → AcquisitionOrderLines
 ├── references → Vendor, Staff
```

---

## 🧭 7. TL;DR Summary

| Aggregate Root       | Child Entities         | Repository                   | Domain Focus             |
| -------------------- | ---------------------- | ---------------------------- | ------------------------ |
| **Branch**           | —                      | `BranchRepository`           | Library locations        |
| **Staff**            | —                      | `StaffRepository`            | Workforce management     |
| **Patron**           | —                      | `PatronRepository`           | Membership + eligibility |
| **Item**             | `Copy`                 | `ItemRepository`             | Bibliographic control    |
| **Serial**           | `SerialIssue`          | `SerialRepository`           | Periodical management    |
| **Loan**             | —                      | `LoanRepository`             | Circulation transaction  |
| **Hold**             | —                      | `HoldRepository`             | Reservation queue        |
| **Fine**             | —                      | `FineRepository`             | Patron penalties         |
| **Vendor**           | —                      | `VendorRepository`           | Supplier management      |
| **AcquisitionOrder** | `AcquisitionOrderLine` | `AcquisitionOrderRepository` | Procurement process      |
