import React, { useState } from "react";
import { Container } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import AuthForm from "./AuthForm";
import { login } from "../../api/auth";

const LogInForm = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState<boolean>(true);
  const navigate = useNavigate();
  // function to handle if algorithm changes
  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    e.preventDefault();
    const { name, value } = e.target;
    switch (name) {
      case "username":
        setUsername(value);
        break;
      case "password":
        setPassword(value);
        break;
      default:
        break;
    }
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setMessage("logging in");
    console.log(loading);
    try {
      const data = await login(username, password);
      setMessage(data.msg);
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("user", JSON.stringify(data.user));
      const userId = data.user.id;
      navigate(`/profile/${userId}`);
    } catch (error) {
      console.error("Login Error", error);
      setMessage("Error Logging in");
    } finally {
      setLoading(false);
    }
  };
  return (
    <Container className="d-flex flex-column justify-content-center align-items-center">
      <div>
        <h1> Log In</h1>
        <AuthForm
          isLogin={true}
          username={username}
          password={password}
          onChange={handleChange}
          onSubmit={handleSubmit}
        />
        {message && <p className="text-danger">{message}</p>}
      </div>
    </Container>
  );
};

export default LogInForm;
