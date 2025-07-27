import { BASE_URL } from "./url";
import type { Order } from "../types/Order";

export const getOrders = async (): Promise<Order[]> => {
  const res = await fetch(`${BASE_URL}/api/orders?status=ready`, {
    headers: {
      "Content-Type": "application/json",
    },
  });
  if (!res.ok) {
    throw new Error("Error fetching orders");
  }
  const data = await res.json();
  return data;
};

export const getOrderDetails = async (order_id: number): Promise<Order> => {
  const res = await fetch(`${BASE_URL}/api/orders/${order_id}`, {
    headers: {
      "Content-Type": "application/json",
    },
  });
  if (!res.ok) {
    throw new Error("Error fetching order details");
  }
  const data = await res.json();
  return data;
};
