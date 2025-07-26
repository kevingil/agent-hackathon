import { BASE_URL } from "./url";

export const getUserPosts = async (userId: number | string, token: string) => {
  const res = await fetch(`${BASE_URL}/posts/${userId}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  if (!res.ok) {
    return new Error("Error");
  }
  const data = await res.json();
  return data.posts;
};

export const getPost = async (userId: number | string, token: string) => {
  const res = await fetch(`${BASE_URL}/post/id=${userId}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  if (!res.ok) {
    return new Error("Error");
  }
  const data = await res.json();
  return data.post;
};

export const searchPosts = async (query: string, token: string) => {
  const res = await fetch(`${BASE_URL}/posts/q=${query}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  if (!res.ok) {
    return new Error("Error");
  }
  const data = await res.json();
  return data.posts;
};

export const deletePost = async (userId: number | string, token: string) => {
  const res = await fetch(`${BASE_URL}/post/id=${userId}`, {
    method: "POST",
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

export const editPost = async (userId: number | string, token: string) => {
  const res = await fetch(`${BASE_URL}/post/id=${userId}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  if (!res.ok) {
    return new Error("Error");
  }
  const data = await res.json();
  return data.post;
};
