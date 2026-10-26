# EcoFit Database Guide

## 1. What Database Does EcoFit Use?
EcoFit uses **Supabase**. Supabase is a cloud database that uses **PostgreSQL**.
It stores user profiles, workouts, water intake, and fruit intake.

---

## 2. Main Tables

### Table 1: `bd_utilizadores` (Users)
Stores account information.
* `utilizador_id`: Number (Primary Key).
* `nome`: Username text.
* `palavra_passe`: User password.
* `estado`: Status (`Pendente`, `Aprovado`, `Rejeitado`).
* `tipo_id`: User type (Linked to `bd_tipos_utilizador`).

### Table 2: `bd_tipos_utilizador` (User Roles)
Stores user types.
* `tipo_id`: Number (Primary Key).
* `descricao`: Role name (`Admin`, `Atleta`, `Atleta Pro`).

### Table 3: `bd_atividades` (Workouts and Habits)
Stores daily physical logs.
* `atividade_id`: Number (Primary Key).
* `utilizador_id`: User owner ID (Foreign Key).
* `km_corridos`: Distance in kilometers.
* `minutos_treino`: Time in minutes.
* `copos_agua`: Glasses of water.
* `pecas_fruta`: Pieces of fruit.
* `pontos_ganhos`: Total points calculated.
* `temperatura`: Local weather temperature in Celsius.

---

## 3. Points Formula
The database stores points using this basic rule:
* 1 km = 10 points
* 1 minute = 1 point
* **Total Points Formula:** `(km * 10) + (minutes * 1)`