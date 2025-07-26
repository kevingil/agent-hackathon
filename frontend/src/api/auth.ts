import { BASE_URL } from "./url";

export const isAuthenticated = () => {
  return !!localStorage.getItem("token"); // or sessionStorage or a context value
};

export const login = async (username: string, password: string) => {
  const res = await fetch(`${BASE_URL}/auth/login`, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) {
    return new Error("Error");
  }
  const data = await res.json();
  return data;
};

export const signup = async (
  username: string,
  email: string,
  password: string
) => {
  const res = await fetch(`${BASE_URL}/auth/signup`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ username, email, password }),
  });
  if (!res.ok) {
    return new Error("Error");
  }
  const data = await res.json();
  return data;
};
