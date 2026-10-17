# Tres Naranjos

Sitio web de Tres Naranjos Triple Sec, de Agave Imports LLC.

## Cómo se publica

Cloudflare publica la carpeta `site/` automáticamente cada vez que hay un cambio nuevo en la rama `main`. No hay que subir nada a mano. Es gratis.

## Cómo hacer cambios

Abre este repositorio en Claude Code y pide el cambio en tus palabras. Por ejemplo:

- "Cambia el número de WhatsApp a 787-555-1234"
- "Añade un trago nuevo: Paloma con Tres Naranjos" (adjunta la foto)
- "Quita La Grieta de la lista de Disponible en"
- "Cambia el dominio a tresnaranjos.com"

Claude sigue las instrucciones de `CLAUDE.md`, revisa que todo se vea bien en celular y computadora, y guarda el cambio. En un minuto está en vivo.

## Si algo sale mal

En Cloudflare, ve a **Workers & Pages → tres-naranjos-web → Deployments**, escoge una versión anterior y usa **Rollback**. El sitio vuelve a como estaba.
