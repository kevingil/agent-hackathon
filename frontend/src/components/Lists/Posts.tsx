import Card from "react-bootstrap/Card";
import { useState, useEffect } from "react";
import PostCard from "../ListItems/PostCard";
import type { Post } from "../../types/Post";
import { getUserPosts } from "../../api/posts";

const Posts = ({ userId }: { userId: number }) => {
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState<boolean>();

  useEffect(() => {
    const fetchPosts = async () => {
      setLoading(true);
      const token = localStorage.getItem("token");
      if (!token || !userId) {
        return;
      }
      try {
        const posts = await getUserPosts(userId, token);
        setPosts(posts);
      } catch (error) {
        console.log(`error ${error}`);
      } finally {
        setLoading(false);
      }
    };
    if (userId) {
      fetchPosts;
    }
  }, []);

  return (
    <>
      <Card style={{ width: "18rem" }}>
        <Card.Body>
          {loading ? (
            <Card.Title>Loading ... </Card.Title>
          ) : posts.length === 0 ? (
            <Card.Title> No Posts </Card.Title>
          ) : (
            posts?.map((post: Post) => <PostCard post={post} key={post.id} />)
          )}
        </Card.Body>
      </Card>
    </>
  );
};

export default Posts;
