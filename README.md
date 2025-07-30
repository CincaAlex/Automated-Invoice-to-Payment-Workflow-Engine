# 🧾 Invoice Manager (Django + React)

This is a full-stack project that combines a **Django REST API backend** with a **React + TypeScript frontend**. The goal of this project is to create a secure and simple platform where authenticated users can upload invoices and view them, while administrators can access additional management features.

## 🚀 Purpose

This project was built to help me learn and apply several core concepts:

- Building and structuring a **RESTful API with Django and Django REST Framework**
- Handling **authentication using JWT**
- Creating a **frontend using React + TypeScript**
- Managing **role-based access control** (admin-only pages)
- Connecting frontend and backend through authenticated HTTP requests

## ✅ Project Status

- **Backend**: ~99% complete  
  - User registration & login (JWT-based)
  - Invoice upload & storage
  - Admin/user role distinction
  - API ready for frontend consumption

- **Frontend**: Work in progress  
  - Authentication
  - Protected routes
  - Basic routing
  - Admin-only route logic done
  - UI/UX not implemented yet

## 🔧 How to Run It Locally

### 1. Clone the repo

### 2. Backend Setup (Django)

#### ✅ Install Dependencies

```bash
python -m venv env
source env\Scripts\activate
pip install -r django djangorestframework djangorestframework-simplejwt corsheaders
```

#### ✅ Run Migrations

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

#### ✅ Create a Superuser (for admin access)

```bash
python manage.py createsuperuser
```

#### ✅ Run the Backend

```bash
python manage.py runserver
```

Your backend API should now be running at `http://localhost:8000`.

### 3. Frontend Setup (React + Vite + TypeScript)

```bash
cd frontend
npm install
```

```
VITE_API_URL=http://localhost:8000
```

Start the dev server:

```bash
npm run dev
```

The frontend will run at `http://localhost:5173`.

## 🔐 Authentication

The app uses JWT tokens (`access` and `refresh`) stored in `localStorage`. The tokens are automatically attached to all requests via an Axios interceptor. If the access token expires, it attempts to refresh using the refresh token.

Admin pages are restricted to users who have `is_staff = True` in Django.

## 📚 Technologies Used

### Backend:
- Django
- Django REST Framework
- SimpleJWT (for authentication)
- CORS Headers
- SQLite (default, can be changed)

### Frontend:
- React
- TypeScript
- Vite
- React Router
- Axios
- jwt-decode

## ✍️ To-Do

- [x] Backend API
- [x] JWT Auth & Refresh
- [x] Role-based routing
- [ ] Frontend login UI
- [ ] Invoice upload UI
- [ ] Admin dashboard
- [ ] Styling and responsiveness
