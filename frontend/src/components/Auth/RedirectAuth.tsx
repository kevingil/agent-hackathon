import React from "react";
import { Navigate } from "react-router-dom";
import { isAuthenticated } from "../../api/auth";

type Props = {
  children: React.ReactNode; // safer than JSX.Element
};

const RedirectIfAuthenticated: React.FC<Props> = ({ children }) => {
  if (isAuthenticated()) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

export default RedirectIfAuthenticated;
