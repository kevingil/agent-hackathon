import { Link } from "react-router-dom";
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import logo from "../assets/order_email_agent.png";

const HomePage: React.FC = () => {
  return (
    <div style={{ minHeight: "80vh", display: "flex", alignItems: "center", justifyContent: "center", background: "linear-gradient(90deg, #e3f0ff 0%, #f8fafd 100%)" }}>
      <Container>
        <Row className="align-items-center">
          <Col md={6} style={{ textAlign: "left" }}>
            <h1 style={{ fontWeight: 800, fontSize: 48, marginBottom: 24, color: "#1a237e" }}>
              Agentic Order Processing & Customer Service
            </h1>
            <p style={{ fontSize: 20, color: "#444", marginBottom: 32 }}>
              Supercharge your operations with an AI-powered order management system. Fast, reliable, and built for modern teams.
            </p>
            <Link to="/orders">
              <button style={{ padding: "16px 40px", fontSize: 20, fontWeight: 700, borderRadius: 8, background: "#1976d2", color: "#fff", border: "none", boxShadow: "0 2px 8px rgba(25,118,210,0.08)", cursor: "pointer" }}>
                View Orders
              </button>
            </Link>
          </Col>
          <Col md={6} style={{ textAlign: "center" }}>
            <img src={logo} alt="Order Agent" style={{ width: 320, maxWidth: "90%", margin: "0 auto", borderRadius: 24, filter: "drop-shadow(0 4px 24px rgba(25,118,210,0.10))" }} />
          </Col>
        </Row>
      </Container>
    </div>
  );
};

export default HomePage;
