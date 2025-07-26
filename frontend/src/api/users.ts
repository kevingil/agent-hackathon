import { BASE_URL } from "./url";

export const getUserProfile = async (userId: string, token: string) => {
  const res = await fetch(`${BASE_URL}/profile/${userId}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  if (!res.ok) {
    return new Error("Error");
  }
  const data = await res.json();
  return data;
};

export const getUser = async (userId: string, token: string) => {
  const res = await fetch(`${BASE_URL}/user/${userId}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  if (!res.ok) {
    return new Error("Error");
  }
  const data = await res.json();
  return data;
};

export const getUserFollowers = async (userId: string, token: string) => {
  const res = await fetch(`${BASE_URL}/followers/${userId}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  if (!res.ok) {
    return new Error("Error");
  }
  const data = await res.json();
  return data.followers;
};

export const searchUsers = async (query: string, token: string) => {
  const res = await fetch(`${BASE_URL}/search/q=${query}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  if (!res.ok) {
    return new Error("Error");
  }
  const data = await res.json();
  return data.users;
};
