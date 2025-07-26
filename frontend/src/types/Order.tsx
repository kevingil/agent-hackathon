// movie type for declaring var types
export type Order = {
  id: number;
  name: string;
  description: string;
  cost: string;
  list_price: string;
  quantity: string;
  created_at: string;
  updated_at: string;
};

// moviecardProps type for declaring var types
export type OrderProps = {
  order: Order;
};
