import Card from "react-bootstrap/Card";
import { useState, useEffect } from "react";
import OrderCard from "../ListItems/OrderCard";
import type { Order } from "../../types/Order";
// import { getOrders } from "../../api/orders";

const Orders = () => {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState<boolean>();

  const sample_orders: Order[] = [
    {
      id: 1,
      name: "Order A",
      description: "Description for Order A",
      cost: "10.00",
      list_price: "12.00",
      quantity: "2",
      created_at: "2025-07-25T12:00:00Z",
      updated_at: "2025-07-25T13:00:00Z",
    },
    {
      id: 2,
      name: "Order B",
      description: "Description for Order B",
      cost: "15.00",
      list_price: "18.00",
      quantity: "3",
      created_at: "2025-07-24T10:30:00Z",
      updated_at: "2025-07-24T11:00:00Z",
    },
  ];

  useEffect(() => {
    const fetchOrders = async () => {
      setLoading(true);

      try {
        setOrders(sample_orders);
      } catch (error) {
        console.log(`error ${error}`);
      } finally {
        setLoading(false);
      }
    };
    fetchOrders();
  }, []);

  return (
    <>
      <Card style={{ width: "18rem" }}>
        <Card.Body>
          {loading ? (
            <Card.Title>Loading ... </Card.Title>
          ) : orders.length === 0 ? (
            <Card.Title> No Orders </Card.Title>
          ) : (
            orders?.map((order: Order) => (
              <OrderCard order={order} key={order.id} />
            ))
          )}
        </Card.Body>
      </Card>
    </>
  );
};

export default Orders;
