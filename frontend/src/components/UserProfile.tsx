import Card from "react-bootstrap/Card";
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Spinner from "react-bootstrap/Spinner";
import { useEffect, useState } from "react";
import type { User } from "../types/User";
import { getUserProfile } from "../api/users";
import { Image } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import { getDefaultPhoto } from "../api/helper";

const UserProfile = ({ userId }: { userId: string }) => {
  const [profile, setProfile] = useState<User>();
  const [loading, setLoading] = useState<boolean>();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchProfile = async () => {
      setLoading(true);
      const token = localStorage.getItem("token");
      console.log("Token from localStorage:", token);
      if (!token || !userId) {
        return;
      }
      try {
        const user = await getUserProfile(userId, token);
        console.log("Fetched user:", user);
        setProfile(user);
      } catch (error) {
        console.error("Error fetching profile:", error);
      } finally {
        setLoading(false);
      }
    };

    if (userId) {
      fetchProfile();
    }
  }, [userId]);

  return (
    <>
      <Container className="py-5">
        <Row className="justify-content-center">
          <Col xs={12} md={8}>
            <Card className="border-0 shadow-sm">
              <Card.Body>
                {loading ? (
                  <div className="text-center py-4">
                    <Spinner animation="border" variant="primary" />
                    <Card.Title className="mt-3">Loading Profile...</Card.Title>
                  </div>
                ) : profile ? (
                  <Row className="align-items-center">
                    <Col xs={4} className="text-center">
                      <Image
                        src={profile.pfp || getDefaultPhoto()}
                        roundedCircle
                        fluid
                        alt="Profile Avatar"
                        className="mb-2"
                        style={{
                          width: "100px",
                          height: "100px",
                          objectFit: "cover",
                        }}
                      />
                    </Col>
                    <Col xs={8}>
                      <h4 className="mb-1">@{profile.username}</h4>
                      <div className="d-flex gap-3 mt-2">
                        <Card.Subtitle
                          onClick={() => navigate(`/friends/${userId}`)}
                          style={{
                            cursor: "pointer",
                            color: "blue",
                            textDecoration: "underline",
                          }}
                        >
                          Friends
                        </Card.Subtitle>
                        <Card.Subtitle
                          onClick={() => navigate(`/edit-profile/${userId}`)}
                          style={{
                            cursor: "pointer",
                            color: "blue",
                            textDecoration: "underline",
                          }}
                        >
                          Edit Profile
                        </Card.Subtitle>
                        <Card.Subtitle
                          onClick={() => navigate(`/new_post/${userId}`)}
                          style={{
                            cursor: "pointer",
                            color: "blue",
                            textDecoration: "underline",
                          }}
                        >
                          New Post
                        </Card.Subtitle>
                      </div>
                    </Col>
                  </Row>
                ) : (
                  <div className="text-center py-4">
                    <Card.Title>No profile data found</Card.Title>
                  </div>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    </>
  );
};

export default UserProfile;
