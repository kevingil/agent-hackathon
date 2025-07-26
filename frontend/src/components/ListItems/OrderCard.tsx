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
          <ListGroup.Item>
            <strong>Description:</strong> {order.description}
          </ListGroup.Item>
          <ListGroup.Item>
            <strong>Corst:</strong> {order.cost}
          </ListGroup.Item>
          <ListGroup.Item>
            <strong>List Price:</strong>
            {order.list_price}
          </ListGroup.Item>
          <ListGroup.Item>
            <strong>Quantity:</strong> {order.quantity}
          </ListGroup.Item>
          <ListGroup.Item>
            <strong>Created At:</strong> {order.created_at}
          </ListGroup.Item>
          <ListGroup.Item>
            <strong>Updated At:</strong> {order.updated_at}
          </ListGroup.Item>
        </ListGroup>
      </Card>
    </>
  );
};

export default OrderCard;
