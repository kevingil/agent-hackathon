import Card from "react-bootstrap/Card";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import type { OrderProps } from "../../types/Order";

const OrderCard: React.FC<OrderProps> = ({ order }) => {
  return (
    <Card style={{ width: "100%" }} className="mb-4">
      <Card.Body>
        <Card.Title>
          {" "}
          <strong>Order Name: </strong>
          {order.name}
        </Card.Title>
      </Card.Body>
      <Row className="justify-content-center">
        <Col md={2}>
          <strong>Description:</strong>
        </Col>
        <Col md={4}>{order.description}</Col>
        <Col md={2}>
          <strong>Cost:</strong>
        </Col>
        <Col md={4}>{order.cost}</Col>
      </Row>
      <Row className="justify-content-center">
        <Col md={2}>
          <strong>List Price:</strong>
        </Col>
        <Col md={4}>{order.list_price}</Col>
        <Col md={2}>
          <strong>Quantity:</strong>
        </Col>
        <Col md={4}>{order.quantity}</Col>
      </Row>
      <Row className="justify-content-center">
        <Col md={2}>
          <strong>Created At:</strong>
        </Col>
        <Col md={4}>{order.created_at}</Col>
        <Col md={2}>
          <strong>Updated At:</strong>
        </Col>
        <Col md={4}>{order.updated_at}</Col>
      </Row>
    </Card>
  );
};

export default OrderCard;
