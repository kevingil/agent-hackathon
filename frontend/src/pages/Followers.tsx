import Followers from "../components/Lists/Followers";
import { useParams } from "react-router-dom";

const FollowersPage: React.FC = () => {
  const { userId } = useParams<{ userId: string }>();

  return (
    <>
      <div className="d-flex vh-100 justify-content-center align-items-center">
        {userId && <Followers userId={userId} />}
      </div>
    </>
  );
};

export default FollowersPage;
