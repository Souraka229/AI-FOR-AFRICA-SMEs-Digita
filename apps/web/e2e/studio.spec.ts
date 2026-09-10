import { expect, test } from "@playwright/test";

test("le Studio expose le golden path sans production", async ({ page }) => {
  await page.goto("/studio");
  await expect(
    page.getByRole("heading", { name: /Décrivez l['’]activité/i }),
  ).toBeVisible();
  await expect(page.getByRole("button", { name: "Lancer le pipeline" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "État live" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Coût estimé" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Audit trail" })).toBeVisible();
  await expect(page.getByText("Preview", { exact: true })).toBeVisible();
  await expect(
    page.getByText(/Rien n['’]est déployé en production sans accord explicite/i),
  ).toBeVisible();
});

test("la boutique wax démo conserve XOF et Mobile Money", async ({ page }) => {
  await page.goto("/t/cadjehoun-wax");
  await expect(page.getByText(/Wax Cadjehoun/i).first()).toBeVisible();
  await expect(page.getByText(/FCFA/i).first()).toBeVisible();
  await expect(page.getByText(/Mobile Money/i).first()).toBeVisible();
});
