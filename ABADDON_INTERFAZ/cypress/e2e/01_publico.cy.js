describe('ABADDON - Pruebas públicas en hosting', () => {
  it('Carga la página principal publicada en PythonAnywhere', () => {
    cy.visit('/')
    cy.get('body').should('be.visible')
    cy.contains(/Abaddon|ABADDON|Store|Inicio|Catálogo|Catalogo/i).should('exist')
    cy.screenshot('01-home-hosting')
  })

  it('Carga el catálogo desde el hosting', () => {
    cy.visit('/catalogo/')
    cy.get('body').should('be.visible')
    cy.contains(/producto|catálogo|catalogo|precio|stock|comprar/i).should('exist')
    cy.screenshot('02-catalogo-hosting')
  })

  it('Carga la página de login', () => {
    cy.visit('/login/')
    cy.get('body').should('be.visible')
    cy.get('input[type="password"]').should('be.visible')
    cy.screenshot('03-login-hosting')
  })
})