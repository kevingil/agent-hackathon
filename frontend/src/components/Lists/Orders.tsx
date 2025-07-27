import { useState, useEffect } from "react";
import OrderCard from "../ListItems/OrderCard";
import type { Order } from "../../types/Order";
import { getOrders } from "../../api/orders";

const Orders = () => {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchOrders = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await getOrders();
        setOrders(data);
      } catch (error: unknown) {
        setError(error instanceof Error ? error.message : "Failed to fetch orders");
      } finally {
        setLoading(false);
      }
    };
    fetchOrders();
  }, []);

  return (
    <div>
      {loading ? (
        <div className="text-center">
          <h2>Loading...</h2>
        </div>
      ) : error ? (
        <div className="text-center text-red-500">
          <h2>{error}</h2>
        </div>
      ) : orders.length === 0 ? (
        <div className="text-center">
          <h2>No Orders</h2>
        </div>
      ) : (
        orders.map((order: Order) => (
          <div key={order.id} className="mb-4">
            <OrderCard order={order} />
          </div>
        ))
      )}
    </div>
  );
};

export default Orders;
