import Link from 'next/link';
import Image from 'next/image';

const ITEMS = [
  { src: '/refs/instant.webp', name: 'Instant.so', use: 'Carte composer, chips de pages, Generate' },
  { src: '/refs/relume.webp', name: 'Relume', use: 'Brief, assembled not generated' },
  { src: '/refs/durable.webp', name: 'Durable', use: 'What type of business are you building' },
  { src: '/refs/replit.webp', name: 'Replit', use: 'Types + example prompts' },
  { src: '/refs/lovable.webp', name: 'Lovable', use: '+ micro, pilule. Pas tout le fold.' },
  { src: '/refs/claude.webp', name: 'Claude', use: 'Champ How can I help you today' },
  { src: '/refs/kkiapay.webp', name: 'KKiaPay', use: 'MoMo Benin, lien WhatsApp' },
  { src: '/refs/wave.webp', name: 'Wave', use: 'QR, FCFA, 1%' },
  { src: '/refs/fedapay.webp', name: 'FedaPay', use: 'Agree BCEAO' },
  { src: '/refs/ligdicash.webp', name: 'LigdiCash', use: 'API + Paylink UEMOA' },
  { src: '/refs/paydunya.webp', name: 'PayDunya', use: 'Paiements digitaux' },
  { src: '/refs/orange-money.webp', name: 'Orange Money', use: 'Encaissement entreprise CI' },
  { src: '/refs/mtn-momo.webp', name: 'MTN MoMo', use: 'API, 60M users' },
  { src: '/refs/yas.webp', name: 'Yas / Mixx', use: 'Operateur Senegal, Mixx dans la nav' },
  { src: '/refs/whatsapp.webp', name: 'WhatsApp Business', use: 'Commande dans la conversation' },
  { src: '/refs/woodin.webp', name: 'Woodin', use: 'Wax pret-a-porter, Cotonou' },
  { src: '/refs/vlisco.webp', name: 'Vlisco', use: 'Boutique tissu reelle' },
  { src: '/refs/glovo.webp', name: 'Glovo', use: 'La barre adresse est le produit' },
  { src: '/refs/fresha.webp', name: 'Fresha', use: 'Recherche traitement + lieu + heure' },
] as const;

export default function RefsPage() {
  return (
    <main className="refs">
      <header className="refs__nav">
        <Link href="/">afrosite</Link>
        <span>Captures live. Rien d invente.</span>
      </header>
      <h1 className="refs__title">References</h1>
      <p className="refs__lede">
        Produits ouverts le 10 septembre 2026. Chaque image sert un element de la landing, pas une vitrine fictive.
      </p>
      <ul className="refs__grid">
        {ITEMS.map((item) => (
          <li key={item.src}>
            <figure>
              <Image src={item.src} alt={item.name} width={640} height={360} />
              <figcaption>
                <strong>{item.name}</strong>
                <span>{item.use}</span>
              </figcaption>
            </figure>
          </li>
        ))}
      </ul>
    </main>
  );
}
