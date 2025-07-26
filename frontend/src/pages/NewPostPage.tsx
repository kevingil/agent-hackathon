import NewPostForm from "../components/Posts/NewPostForm";
import { useParams } from "react-router-dom";

// home component
const NewPostPage: React.FC = () => {
  const { userId } = useParams();

  return (
    <div className="home">
      {userId ? <NewPostForm /> : <p>User ID not found.</p>}{" "}
    </div>
  );
};

export default NewPostPage;
