import "../css/Home.css";
import HomeBanner from "../components/Home/HomeBanner";
import FeaturesSection from "../components/Home/FeatureSection";
import AboutSection from "../components/Home/AboutSection";
import Testimonials from "../components/Home/Testimonials";
const ProfilePage: React.FC = () => {
  return (
    <>
      <HomeBanner />
      <FeaturesSection />
      <AboutSection />
      <Testimonials />
    </>
  );
};

export default ProfilePage;
