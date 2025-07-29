import React, { useState, useEffect } from "react"
import { Navigate } from "react-router-dom"
import { jwtDecode } from "jwt-decode"
import api from "../api/api"
import { REFRESH_TOKEN, ACCESS_TOKEN } from "../api/constants"
import type { ReactNode } from "react"

interface ProtectedRouteProps {
  children: ReactNode;
  adminOnly?: boolean;
}

function ProtectedRoute({ children, adminOnly = false }: ProtectedRouteProps) {
  const [isAuthorized, setIsAuthorized] = useState<boolean | null>(null);

  useEffect(() => {
    const auth = async () => {
      const token = localStorage.getItem("ACCESS_TOKEN");
      if (!token) {
        setIsAuthorized(false);
        return;
      }
      try {
        const decoded: any = jwtDecode(token);
        const now = Date.now() / 1000;

        if (decoded.exp < now) {
          // TODO: refresh token or force logout
          setIsAuthorized(false);
          return;
        }

        if (adminOnly && !decoded.isAdmin) {
          setIsAuthorized(false);
          return;
        }

        setIsAuthorized(true);
      } catch {
        setIsAuthorized(false);
      }
    };

    auth();
  }, [adminOnly]);

  if (isAuthorized === null) {
    return <div>Loading...</div>;
  }

  return isAuthorized ? <>{children}</> : <Navigate to="/login" />;
}

export default ProtectedRoute;
