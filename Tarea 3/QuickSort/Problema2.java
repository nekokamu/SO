package QuickSort;
import java.time.LocalTime;
import static java.time.temporal.ChronoUnit.MICROS;

public class Problema2 {
    /*
    public static void quickSortThreads(int[] arreglo, int inicio, int fin) {
        if(fin <= inicio) {
            return;
        }
        int pivote = particion(arreglo, inicio, fin);

        Problema2 izq = new Problema2();
        Thread t_izq = new Thread(izq);
        t_izq.start();
        
        Problema2 der = new Problema2();
        Thread t_der = new Thread(der);
        t_der.start();
        
        quickSortThreads(arreglo, inicio, pivote-1);
        quickSortThreads(arreglo, pivote+1, fin);
    }*/

    public static void main (String[] args) {

        // Crear arreglo de prueba
        int n = 10;
        int[] arreglo, arreglo_aux;
        int min = 0;
        int max = 100;
        double random;
        arreglo = new int[n];
        arreglo_aux = new int[n];
        for(int i = 0; i < n; i++) {
            random = Math.random()*(max-min+1)+min;
            arreglo[i] = arreglo_aux[i] = (int)random;
        }

        // Imprimir arreglo de Prueba
        System.out.println("-------------------");
        System.out.println("Arreglo:\n");
        for(int i = 0; i < n; i++) {
            System.out.println(arreglo[i] );
        }
        System.out.println("\n-------------------");
        
        // Instanciar hilo de QuickSort
        Thread t = new Thread(new QuickSortThread(arreglo, 0, n-1));
        System.out.println("Arreglo ordenado con Threads: \n");
        // Ejecución de Sort (con threads) y calculo de su tiempo de ejecucion
        // El arreglo ordenado se imprime desde la misma clase
        LocalTime tiempo_inicio = LocalTime.now();
        t.start();
        try{t.join();}catch(Exception e){};
        LocalTime tiempo_fin = LocalTime.now();

        System.out.println();
        System.out.println("Tiempo de inicio: " + tiempo_inicio);
        System.out.println("Tiempo de fin:    "+ tiempo_fin);        
        System.out.println("Tiempo de ejecución (microsegundos): " + MICROS.between(tiempo_inicio, tiempo_fin));
        
        //----------------------------------------------------------------
        System.out.println("\n-------------------");
        System.out.println("Arreglo ordenado: \n");

        QuickSortSimple qs = new QuickSortSimple();
        tiempo_inicio = LocalTime.now();
        qs.quickSort(arreglo,0,n-1);
        tiempo_fin = LocalTime.now();
        for(int i = 0; i < n; i++) {
            System.out.println(arreglo[i] );
        }
        System.out.println();
        System.out.println("Tiempo de inicio: " + tiempo_inicio);
        System.out.println("Tiempo de fin:    "+ tiempo_fin);        
        System.out.println("Tiempo de ejecución (microsegundos): " + MICROS.between(tiempo_inicio, tiempo_fin));
        

    }
}
