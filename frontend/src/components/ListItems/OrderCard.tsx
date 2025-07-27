import Card from "react-bootstrap/Card";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import type { OrderProps } from "../../types/Order";

const OrderCard: React.FC<OrderProps> = ({ order }) => {
  return (
    <Card style={{ width: "100%" }} className="mb-4">
      <Card.Body>
        <Card.Title>
          <strong>Order ID: </strong>
          {order.id}
        </Card.Title>
        <Row className="mb-2">
          <Col md={4}><strong>Status:</strong> {order.status}</Col>
          <Col md={4}><strong>Total Amount:</strong> ${order.total_amount.toFixed(2)}</Col>
        </Row>
        <Row className="mb-2">
          <Col md={4}><strong>Created At:</strong> {order.created_at}</Col>
          <Col md={4}><strong>Updated At:</strong> {order.updated_at}</Col>
        </Row>
        {order.items && order.items.length > 0 && (
          <div className="mt-3">
            <h5>Order Items</h5>
            <table className="table table-sm">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Quantity</th>
                  <th>Unit Price</th>
                  <th>Total Price</th>
                </tr>
              </thead>
              <tbody>
                {order.items.map((item) => (
                  <tr key={item.id}>
                    <td>{item.name}</td>
                    <td>{item.quantity}</td>
                    <td>${item.unit_price.toFixed(2)}</td>
                    <td>${item.total_price.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card.Body>
    </Card>
  );
};

export default OrderCard;
