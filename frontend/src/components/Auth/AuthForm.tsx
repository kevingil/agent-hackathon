import { Form } from "react-bootstrap";
import type { AuthFormProps } from "../../types/AuthFormProp.ts";

const AuthForm: React.FC<AuthFormProps> = ({
  isLogin,
  username,
  password,
  email,
  onChange,
  onSubmit,
}) => (
  <Form onSubmit={onSubmit} className="p-3 border rounded bg-light shadow">
    <Form.Label className="fw-bold">Username</Form.Label>
    <Form.Control
      type="text"
      name="username"
      value={username}
      onChange={onChange}
      required
    />

    {!isLogin && (
      <>
        <Form.Label className="fw-bold">Email</Form.Label>
        <Form.Control
          type="text"
          name="email"
          value={email}
          onChange={onChange}
          required
        />
      </>
    )}

    <Form.Label className="fw-bold">Password</Form.Label>
    <Form.Control
      type="text"
      name="password"
      value={password}
      onChange={onChange}
      required
    />
    <button type="submit" className="btn btn-primary">
      {isLogin ? "Login" : "Sign Up"}
    </button>
  </Form>
);

export default AuthForm;
