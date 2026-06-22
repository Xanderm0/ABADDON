Cypress.Commands.add('login', (email, password) => {
  cy.visit('/login/')

  cy.get('input[name="email"], input[name="username"], input[type="email"], input[type="text"]')
    .first()
    .clear()
    .type(email)

  cy.get('input[name="password"], input[type="password"]')
    .first()
    .clear()
    .type(password)

  cy.get('button[type="submit"], input[type="submit"]')
    .first()
    .click()
})