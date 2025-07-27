import { Navbar, Nav, Container } from "react-bootstrap";
import { Link, useLocation } from "react-router-dom";
import logo from "../../assets/order_email_agent.png";

const Navigation = () => {
  const location = useLocation();
  return (
    <Navbar
      bg="white"
      variant="light"
      expand="md"
      collapseOnSelect
      className="shadow-sm"
      style={{ padding: "0.25rem 0" }}
    >
      <Container>
        <Navbar.Brand as={Link} to="/" style={{ display: "flex", alignItems: "center", gap: 0 }}>
          <img src={logo} alt="Logo" width="100" height="50" style={{ objectFit: "contain" }} />
          <span style={{ fontWeight: 700, fontSize: 20, color: "#222" }}>OrderMail</span>
        </Navbar.Brand>
        <Navbar.Toggle aria-controls="navbar-nav" />
        <Navbar.Collapse id="navbar-nav">
          <Nav className="ms-auto" style={{ fontWeight: 600, fontSize: 18 }}>
            <Nav.Link as={Link} to="/orders" active={location.pathname === "/orders"} style={{ color: location.pathname === "/orders" ? "#007bff" : undefined }}>
              Orders
            </Nav.Link>
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default Navigation;
