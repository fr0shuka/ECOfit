# EcoFit Code Style Guide

## 1. Introduction
This guide shows how to write clean Python code for the EcoFit app. 
Clean code is easy to read and easy to fix.

---

## 2. General Python Rules
* Use **Python 3**.
* Write clear variable names in Portuguese or English.
* Keep functions small and simple. One function does one job.

---

## 3. File Names and Folders
Organize code into simple folders:
* `app.py`: Main Streamlit app file.
* `models/`: Files that talk to the database (e.g., `user_model.py`, `activity_model.py`).
* `controllers/`: Files that process data and logic (e.g., `file_controller.py`, `weather_controller.py`).
* `views/`: Files that draw pages and forms (e.g., `users_view.py`).

---

## 4. Easy Naming Examples
* **Classes:** Use CamelCase. Example: `UserModel`, `ActivityModel`.
* **Functions:** Use lowercase with underscores. Example: `buscar_por_nome()`, `salvar_atividade()`.
* **Variables:** Use clear names. Example: `total_kms`, `id_utilizador`.

---

## 5. Comments and Errors
* Write simple comments to explain hard parts.
* Always use `try / except` blocks when loading files or calling external APIs to prevent the app from crashing.