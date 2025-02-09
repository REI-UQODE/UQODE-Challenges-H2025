import java.util.*;

public class StarChallenge {

    private static final Map<Character, String[]> motifs = new HashMap<>();
    private static final Random random = new Random();
    private static final String[] couleurs = {"\u001B[31m", "\u001B[32m", "\u001B[33m", "\u001B[34m", "\u001B[35m", "\u001B[36m"};
    private static final String resetCouleur = "\u001B[0m";

    static {
        motifs.put('A', new String[] {
            "  *  ",
            " * * ",
            "*****",
            "*   *",
            "*   *"
        });
        motifs.put('B', new String[] {
            "**** ",
            "*   *",
            "**** ",
            "*   *",
            "**** "
        });
        motifs.put('C', new String[] {
            " ****",
            "*    ",
            "*    ",
            "*    ",
            " ****"
        });
        motifs.put('D', new String[] {
            "**** ",
            "*   *",
            "*   *",
            "*   *",
            "**** "
        });
        motifs.put('E', new String[] {
            "*****",
            "*    ",
            "**** ",
            "*    ",
            "*****"
        });
        motifs.put('F', new String[] {
            "*****",
            "*    ",
            "**** ",
            "*    ",
            "*    "
        });
        motifs.put('G', new String[] {
            " ****",
            "*    ",
            "*  **",
            "*   *",
            "*****"
        });
        motifs.put('H', new String[] {
            "*   *",
            "*   *",
            "*****",
            "*   *",
            "*   *"
        });
        motifs.put('I', new String[] {
            "*****",
            "  *  ",
            "  *  ",
            "  *  ",
            "*****"
        });
        motifs.put('J', new String[] {
            "*****",
            "   * ",
            "   * ",
            "*  * ",
            " *** "
        });
        motifs.put('K', new String[] {
            "*   *",
            "*  * ",
            "***  ",
            "*  * ",
            "*   *"
        });
        motifs.put('L', new String[] {
            "*    ",
            "*    ",
            "*    ",
            "*    ",
            "*****"
        });
        motifs.put('M', new String[] {
            "*   *",
            "** **",
            "* * *",
            "*   *",
            "*   *"
        });
        motifs.put('N', new String[] {
            "*   *",
            "**  *",
            "* * *",
            "*  **",
            "*   *"
        });
        motifs.put('O', new String[] {
            " *** ",
            "*   *",
            "*   *",
            "*   *",
            " *** "
        });
        motifs.put('P', new String[] {
            "**** ",
            "*   *",
            "**** ",
            "*    ",
            "*    "
        });
        motifs.put('Q', new String[] {
            " **** ",
            "*    *",
            "* *  *",
            "*  * *",
            " ** *"
        });
        motifs.put('R', new String[] {
            "**** ",
            "*   *",
            "**** ",
            "*  * ",
            "*   *"
        });
        motifs.put('S', new String[] {
            " ****",
            "*    ",
            " *** ",
            "    *",
            "**** "
        });
        motifs.put('T', new String[] {
            "*****",
            "  *  ",
            "  *  ",
            "  *  ",
            "  *  "
        });
        motifs.put('U', new String[] {
            "*   *",
            "*   *",
            "*   *",
            "*   *",
            " *** "
        });
        motifs.put('V', new String[] {
            "*   *",
            "*   *",
            "*   *",
            " * * ",
            "  *  "
        });
        motifs.put('W', new String[] {
            "*   *   *",
            "*   *   *",
            "*   *   *",
            " * * * * ",
            "  *   *  "
        });
        motifs.put('X', new String[] {
            "*   *",
            " * * ",
            "  *  ",
            " * * ",
            "*   *"
        });
        motifs.put('Y', new String[] {
            "*   *",
            " * * ",
            "  *  ",
            "  *  ",
            "  *  "
        });
        motifs.put('Z', new String[] {
            "*****",
            "   * ",
            "  *  ",
            " *   ",
            "*****"
        });
        motifs.put(' ', new String[] {
            "   ",
            "   ",
            "   ",
            "   ",
            "   "
        });
        motifs.put('-', new String[] {
            "   ",
            "   ",
            "***",
            "   ",
            "   "
        });
        motifs.put('.', new String[] {
            " ",
            " ",
            " ",
            " ",
            "*"
        });
        motifs.put(',', new String[] {
            "  ",
            "  ",
            "  ",
            " *",
            "* "
        });
        motifs.put('!', new String[] {
            " * ",
            " * ",
            " * ",
            "   ",
            " * "
        });
        motifs.put('?', new String[] {
            " *** ",
            "*   *",
            "  ** ",
            "     ",
            "  *  "
        });
        motifs.put(':', new String[] {
            "    ",
            "  * ",
            "    ",
            "  * ",
            "    "
        });
    }

    public static String transformerEnEtoiles(String phrase, int maxLargeur) {
        phrase = phrase.toUpperCase();
        List<StringBuilder[]> lignesGroupes = new ArrayList<>();
        StringBuilder[] lignesEtoiles = {
            new StringBuilder(), new StringBuilder(), new StringBuilder(), new StringBuilder(), new StringBuilder()
        };
        int largeurActuelle = 0;

        for (char lettre : phrase.toCharArray()) {
            if (motifs.containsKey(lettre)) {
                String[] motif = motifs.get(lettre);

                if (largeurActuelle + motif[0].length() > maxLargeur) {
                    lignesGroupes.add(lignesEtoiles);
                    lignesEtoiles = new StringBuilder[] {
                        new StringBuilder(), new StringBuilder(), new StringBuilder(), new StringBuilder(), new StringBuilder()
                    };
                    largeurActuelle = 0;
                }

                for (int i = 0; i < 5; i++) {
                    lignesEtoiles[i].append(motif[i]).append("  ");
                }
                largeurActuelle += motif[0].length() + 2;
            }
        }

        lignesGroupes.add(lignesEtoiles);
        StringBuilder resultat = new StringBuilder();
        for (StringBuilder[] groupe : lignesGroupes) {
            for (StringBuilder ligne : groupe) {
                resultat.append(ligne).append("\n");
            }
            resultat.append("\n");
        }
        return resultat.toString();
    }

    public static void afficherAvecCouleurEtAnimation(String texte, int delai) throws InterruptedException {
        String[] lignes = texte.split("\n");
        StringBuilder animationBuffer = new StringBuilder();

        for (String ligne : lignes) {
            String couleur = couleurs[random.nextInt(couleurs.length)];
            animationBuffer.append(couleur).append(ligne).append(resetCouleur).append("\n");
            System.out.print(animationBuffer.toString());
            animationBuffer.setLength(0);
            Thread.sleep(delai);
        }
    }

    public static void main(String[] args) throws InterruptedException {
        Scanner scanner = new Scanner(System.in);
        String phrase;
        int maxLargeur = 150;

        do {
            System.out.println("Entrez une phrase (ou tapez 'exit' pour quitter) :");
            phrase = scanner.nextLine();
            if (!phrase.equalsIgnoreCase("exit")) {
                String etoiles = transformerEnEtoiles(phrase, maxLargeur);
                afficherAvecCouleurEtAnimation(etoiles, 200);
            }
        } while (!phrase.equalsIgnoreCase("exit"));

        System.out.println("Au revoir !");
    }
}
