# EcoFit Security Guide (A1 Level)

## 1. Introduction
This file explains how EcoFit protects user data and system files. 
EcoFit keeps your information safe using passwords, roles, and admin checks.

---

## 2. User Roles
There are two types of users in EcoFit:
* **Athlete (Atleta):** A normal user. They can log workouts, see their points, and check rankings.
* **Admin:** A manager. They can approve new users, block accounts, and manage system data.

---

## 3. Account Approval Process
When a new person registers on EcoFit, they cannot log in immediately.
1. **Registration:** The new user creates a username and password.
2. **Pending Status:** The account status becomes `Pendente` (Pending).
3. **Admin Check:** An Admin looks at the user list.
4. **Approval:** The Admin changes the status to `Aprovado` (Approved). Now the user can log in!

---

## 4. Login and Password Rules
* **Login Check:** The app checks the username, password, and status before letting anyone in.
* **Bad Passwords:** If the password is wrong, the system shows an error message.
* **Pending Users:** If a user is pending, the system says "Awaiting Approval".

---

## 5. Data Protection
* **Secret Keys:** API keys and database passwords are hidden in Streamlit secrets files (`secrets.toml`).
* **Database Safety:** Each workout is linked to a specific user ID. Users only manage their own health data.