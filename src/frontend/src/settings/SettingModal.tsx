import React, { useState, useEffect, useCallback } from "react";
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";
import Form from "react-bootstrap/Form";
import Tabs from "react-bootstrap/Tabs";
import Tab from "react-bootstrap/Tab";

// Added for colour adjustments
const ColourAdjustments = [
  ["none", "Default"],
  ["redgreen", "Protanopia/Deuteranopia-friendly"],
  ["tritanopia", "Tritanopia-friendly"],
  ["achromatopsia", "Achromatopsia-friendly"],
];

// Define the types for the props expected by the SettingModal component
interface SettingModalProps {
  show: boolean;
  setShow: React.Dispatch<React.SetStateAction<boolean>>;
}

// The SettingModal component manages accessibility settings for the application.
const SettingModal: React.FC<SettingModalProps> = ({ show, setShow }) => {
  // State to track the currently active colour view.
  const [activeView, setActiveView] = useState<string>(
    sessionStorage.getItem("activeAccessibilityView") ??
      ColourAdjustments[0][0],
  );
  // Separate states for each font setting.
  const [isLargeFont, setIsLargeFont] = useState<boolean>(
    sessionStorage.getItem("largeFontEnabled") === "true",
  );
  const [isDyslexicFont, setIsDyslexicFont] = useState<boolean>(
    sessionStorage.getItem("dyslexicFontEnabled") === "true",
  );

  // State to enable/disable the save button.
  const [isSaveDisabled, setIsSaveDisabled] = useState<boolean>(true);

  // Set the saved settings to the selected ones
  function saveSettings() {
    sessionStorage.setItem("activeAccessibilityView", activeView);
    sessionStorage.setItem("largeFontEnabled", String(isLargeFont));
    sessionStorage.setItem("dyslexicFontEnabled", String(isDyslexicFont));
    applySettings();
  }

  const applySettings = useCallback(() => {
    document.body.setAttribute("data-colour-view", activeView);
    document.body.classList.toggle("dyslexic-font", isDyslexicFont);
    document.documentElement.classList.toggle("large-font", isLargeFont);
  }, [activeView, isDyslexicFont, isLargeFont]);

  // Set selected settings to reflect the saved ones
  function getSettings() {
    setActiveView(
      sessionStorage.getItem("activeAccessibilityView") ??
        ColourAdjustments[0][0],
    );
    setIsLargeFont(sessionStorage.getItem("largeFontEnabled") === "true");
    setIsDyslexicFont(sessionStorage.getItem("dyslexicFontEnabled") === "true");
  }

  // Handler for selecting a colour view.
  function changeSetting(callback: () => void) {
    callback();
    setIsSaveDisabled(false); // Enable the save button as a change has been made
  }

  // Handler for saving the current settings to sessionStorage
  function handleSaveAndClose() {
    saveSettings();
    handleClose();
    window.location.reload();
  }

  // Handler for closing the modal, optionally
  function handleClose() {
    getSettings();
    setShow(false);
  }

  // Load the saved accessibility settings from sessionStorage when the modal is shown
  useEffect(() => {
    getSettings();
    applySettings();
  }, [show]);

  return (
    <Modal show={show} onHide={handleClose}>
      <Modal.Header closeButton>
        <Modal.Title>Accessibility Settings</Modal.Title>
      </Modal.Header>
      <Modal.Body className="px-0">
        <Tabs
          defaultActiveKey="colour"
          id="accessibility-settings-tabs"
          className="d-flex gap-2 px-3"
        >
          <Tab eventKey="colour" title="Colour Adjustments" className="p-3">
            <Form>
              {ColourAdjustments.map(([viewName, displayName]) => (
                <Form.Check
                  key={viewName}
                  type="radio"
                  role="button"
                  id={`colour-${viewName}`}
                  label={displayName}
                  name="accessibilityView"
                  checked={activeView === viewName}
                  onChange={() => changeSetting(() => setActiveView(viewName))}
                />
              ))}
            </Form>
          </Tab>
          <Tab eventKey="font" title="Font Adjustments" className="p-3">
            <Form>
              <Form.Check
                type="switch"
                id="font-large"
                className="fw-bold"
                label="Large Font"
                checked={isLargeFont}
                onChange={() =>
                  changeSetting(() => setIsLargeFont(!isLargeFont))
                }
              />
              <Form.Check
                type="switch"
                id="font-dyslexic"
                className="dyslexic-font"
                label="Dyslexia-friendly Font"
                checked={isDyslexicFont}
                onChange={() =>
                  changeSetting(() => setIsDyslexicFont(!isDyslexicFont))
                }
              />
            </Form>
          </Tab>
        </Tabs>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={handleClose}>
          Close
        </Button>
        <Button
          variant="primary"
          onClick={handleSaveAndClose}
          disabled={isSaveDisabled}
        >
          Save & Close
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default SettingModal;
