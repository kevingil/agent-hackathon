import "../css/Home.css";
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Orders from "../components/Lists/Orders";

const HomePage: React.FC = () => {
  return (
    <Container fluid>
      <Row>
        <Col md={12}>
          <h1 className="text-center mt-5">Agentic Order Management System</h1>
          <p className="text-center mb-5">
            This system allows you to view orders created by your AI agents
            effectively.
          </p>
        </Col>
      </Row>
      <Row>
        <Col md={12}>
          <h2 className="text-center mb-5">Recent Orders</h2>
          <Orders />
        </Col>
      </Row>
    </Container>
  );
};

export default HomePage;
