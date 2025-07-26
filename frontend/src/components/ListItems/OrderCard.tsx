import Card from "react-bootstrap/Card";
import ListGroup from "react-bootstrap/ListGroup";
import type { OrderProps } from "../../types/Order";

const OrderCard: React.FC<OrderProps> = ({ order }) => {
  return (
    <>
      <Card style={{ width: "18rem" }}>
        <Card.Body>
          <Card.Title>{order.name}</Card.Title>
        </Card.Body>
        <ListGroup className="list-group-flush">
          <ListGroup.Item>{order.description}</ListGroup.Item>
          <ListGroup.Item>{order.cost}</ListGroup.Item>
          <ListGroup.Item>{order.list_price}</ListGroup.Item>
          <ListGroup.Item>{order.quantity}</ListGroup.Item>
          <ListGroup.Item>{order.created_at}</ListGroup.Item>
          <ListGroup.Item>{order.updated_at}</ListGroup.Item>
        </ListGroup>
      </Card>
    </>
  );
};

export default OrderCard;
