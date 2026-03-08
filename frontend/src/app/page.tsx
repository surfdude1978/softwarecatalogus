import Link from "next/link";

export default function HomePage() {
  return (
    <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
      {/* Hero */}
      <section className="text-center">
        <h1 className="text-4xl font-bold tracking-tight text-primary-500 sm:text-5xl">
          Softwarecatalogus
        </h1>
        <p className="mx-auto mt-6 max-w-2xl text-lg text-gray-600">
          Het centrale platform voor Nederlandse gemeenten om software te
          registreren, vergelijken en raadplegen.
        </p>
        <div className="mt-10 flex items-center justify-center gap-x-6">
          <Link
            href="/pakketten"
            className="rounded-md bg-primary-500 px-6 py-3 text-sm font-semibold text-white shadow-sm hover:bg-primary-600 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-500"
          >
            Bekijk de catalogus
          </Link>
          <Link
            href="/organisaties"
            className="text-sm font-semibold text-gray-900 hover:text-primary-500"
          >
            Organisaties bekijken <span aria-hidden="true">&rarr;</span>
          </Link>
        </div>
      </section>

      {/* Features */}
      <section className="mt-24 grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
        <FeatureCard
          title="Catalogus doorzoeken"
          description="Zoek en filter pakketten op naam, leverancier, standaarden en GEMMA-componenten."
        />
        <FeatureCard
          title="Gluren bij de buren"
          description="Bekijk welke software andere gemeenten gebruiken en leer van hun ervaringen."
        />
        <FeatureCard
          title="GEMMA architectuur"
          description="Bekijk uw pakketlandschap op de GEMMA-referentiearchitectuur kaart."
        />
      </section>
    </div>
  );
}

function FeatureCard({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      <h3 className="text-lg font-semibold text-primary-500">{title}</h3>
      <p className="mt-2 text-sm text-gray-600">{description}</p>
    </div>
  );
}
