import React from "react"
import { BrowserRouter, Routes, Route, Navigate} from "react-router-dom"
import Login from "./pages/login"
import Home from "./pages/home"
import Admin from "./pages/admin"
import NotFound from "./pages/NotFound"
import ProtectedRoute from "./components/ProtectedRoute"

function Logout() {
  localStorage.clear()
  return <Navigate to="/login"/>
}

function App() {

  return (
    <BrowserRouter>
      <Route>
        <Route 
          path="/"
          element={
            <ProtectedRoute>
              <Home />
            </ProtectedRoute>
          }
        />
        <Route 
          path="/admin"
          element={
            <ProtectedRoute adminOnly>
              <Admin />
            </ProtectedRoute>
          }
        />
        <Route 
          path="/login" element={<Login />}
        />
        <Route 
          path="*" element={<NotFound />}
        />
      </Route>
    </BrowserRouter>
  )
}

export default App
