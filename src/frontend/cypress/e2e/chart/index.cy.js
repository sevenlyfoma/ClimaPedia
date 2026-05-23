/// <reference types="cypress" />

describe("chart", () => {
  beforeEach(() => {
    cy.interceptManifest();
    cy.interceptData();
    cy.visit("/chart");
    cy.get("#chart-preview").as("preview");
  });

  it("should show chart previews", () => {
    cy.get("@preview").find(".preview-chart").should("have.length", 5);
  });

  it("should allow previewing", () => {
    cy.get("@preview").find(".preview-chart").eq(0).click();
    cy.location().should((loc) => {
      expect(loc.search).to.eq("?views=1.pie");
    });
    cy.get("#legendBox button").click();
    cy.get("#legendBox").contains("pie").click();

    cy.get("@preview").find(".preview-chart").should("have.length", 5);
  });
});
