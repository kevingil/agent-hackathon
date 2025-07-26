import { BASE_URL } from "./url";

export const getOrders = async (order_id: string) => {
  const res = await fetch(`${BASE_URL}/orders/${order_id}`, {
    headers: {
      "Content-Type": "application/json",
    },
  });
  if (!res.ok) {
    return new Error("Error");
  }
  const data = await res.json();
  return data.orders;
};
